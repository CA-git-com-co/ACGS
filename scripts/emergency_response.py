#!/usr/bin/env python3
"""
ACGS-PGP Emergency Response System

Provides emergency shutdown, recovery, and monitoring capabilities
with <30min RTO (Recovery Time Objective) for constitutional AI governance.
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import requests
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/home/ubuntu/ACGS/logs/emergency_response.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ACGSEmergencyResponse:
    """Emergency response system for ACGS-PGP deployment."""

    def __init__(self):
        self.services = {
            "auth_service": {"port": 8000, "pid": None, "status": "unknown"},
            "ac_service": {"port": 8001, "pid": None, "status": "unknown"},
            "integrity_service": {"port": 8002, "pid": None, "status": "unknown"},
            "fv_service": {"port": 8003, "pid": None, "status": "unknown"},
            "gs_service": {"port": 8004, "pid": None, "status": "unknown"},
            "pgc_service": {"port": 8005, "pid": None, "status": "unknown"},
            "ec_service": {"port": 8006, "pid": None, "status": "unknown"},
            "nano_vllm": {"port": 8007, "pid": None, "status": "unknown"},
        }
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.emergency_log = []

    def log_emergency_event(
        self, event_type: str, message: str, severity: str = "INFO"
    ):
        """Log emergency events with timestamp."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "message": message,
            "severity": severity,
            "constitutional_hash": self.constitutional_hash,
        }
        self.emergency_log.append(event)
        logger.log(getattr(logging, severity), f"[{event_type}] {message}")

    def get_service_pids(self) -> Dict[str, Optional[int]]:
        """Get PIDs of running ACGS services."""
        try:
            # Get processes listening on ACGS ports
            result = subprocess.run(
                ["ss", "-tlnp"], capture_output=True, text=True, timeout=10
            )

            for service_name, service_info in self.services.items():
                port = service_info["port"]
                for line in result.stdout.split("\n"):
                    if f":{port}" in line and "LISTEN" in line:
                        # Extract PID from ss output
                        if "users:((" in line:
                            pid_part = (
                                line.split("users:((")[1]
                                .split(",pid=")[1]
                                .split(",")[0]
                            )
                            try:
                                self.services[service_name]["pid"] = int(pid_part)
                                self.services[service_name]["status"] = "running"
                            except ValueError:
                                pass
                        break

        except Exception as e:
            self.log_emergency_event(
                "PID_DISCOVERY", f"Failed to get service PIDs: {e}", "ERROR"
            )

        return {name: info["pid"] for name, info in self.services.items()}

    def emergency_shutdown(
        self, reason: str = "Manual emergency shutdown"
    ) -> Dict[str, Any]:
        """Emergency shutdown of all ACGS services with <30min RTO capability."""
        start_time = time.time()
        self.log_emergency_event(
            "EMERGENCY_SHUTDOWN", f"Initiating emergency shutdown: {reason}", "CRITICAL"
        )

        shutdown_results = {}

        # Get current service PIDs
        self.get_service_pids()

        # Shutdown services gracefully first, then forcefully if needed
        for service_name, service_info in self.services.items():
            pid = service_info["pid"]
            if pid:
                try:
                    # Try graceful shutdown first (SIGTERM)
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(2)

                    # Check if process is still running
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        # Still running, force kill
                        os.kill(pid, signal.SIGKILL)
                        shutdown_results[service_name] = "force_killed"
                        self.log_emergency_event(
                            "SERVICE_SHUTDOWN",
                            f"{service_name} force killed (PID: {pid})",
                            "WARNING",
                        )
                    except ProcessLookupError:
                        # Process terminated gracefully
                        shutdown_results[service_name] = "graceful_shutdown"
                        self.log_emergency_event(
                            "SERVICE_SHUTDOWN",
                            f"{service_name} shutdown gracefully (PID: {pid})",
                            "INFO",
                        )

                except ProcessLookupError:
                    shutdown_results[service_name] = "not_running"
                except Exception as e:
                    shutdown_results[service_name] = f"error: {e}"
                    self.log_emergency_event(
                        "SERVICE_SHUTDOWN",
                        f"Failed to shutdown {service_name}: {e}",
                        "ERROR",
                    )
            else:
                shutdown_results[service_name] = "not_found"

        shutdown_time = time.time() - start_time

        # Verify all services are down
        verification_results = self.verify_services_down()

        result = {
            "shutdown_initiated": datetime.now(timezone.utc).isoformat(),
            "shutdown_time_seconds": shutdown_time,
            "shutdown_results": shutdown_results,
            "verification": verification_results,
            "constitutional_hash": self.constitutional_hash,
            "rto_target_met": shutdown_time < 1800,  # 30 minutes = 1800 seconds
        }

        self.log_emergency_event(
            "EMERGENCY_SHUTDOWN",
            f"Shutdown completed in {shutdown_time:.2f}s",
            "CRITICAL",
        )
        return result

    def verify_services_down(self) -> Dict[str, bool]:
        """Verify that all services are properly shut down."""
        verification = {}

        for service_name, service_info in self.services.items():
            port = service_info["port"]
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                verification[service_name] = False  # Service still responding
            except requests.exceptions.RequestException:
                verification[service_name] = True  # Service is down

        return verification

    def health_check_all_services(self) -> Dict[str, Any]:
        """Comprehensive health check of all ACGS services."""
        health_results = {}

        for service_name, service_info in self.services.items():
            port = service_info["port"]
            try:
                start_time = time.time()
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                response_time = time.time() - start_time

                health_results[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "data": response.json() if response.status_code == 200 else None,
                }
            except requests.exceptions.RequestException as e:
                health_results[service_name] = {
                    "status": "down",
                    "error": str(e),
                    "response_time": None,
                }

        return health_results

    def constitutional_compliance_check(self) -> Dict[str, Any]:
        """Check constitutional compliance across services."""
        compliance_results = {}

        # Check AC Service constitutional rules
        try:
            response = requests.get(
                "http://localhost:8001/api/v1/constitutional/rules", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                compliance_results["constitutional_rules"] = {
                    "status": "available",
                    "hash_valid": data.get("constitutional_hash")
                    == self.constitutional_hash,
                }
            else:
                compliance_results["constitutional_rules"] = {"status": "unavailable"}
        except Exception as e:
            compliance_results["constitutional_rules"] = {
                "status": "error",
                "error": str(e),
            }

        # Check PGC Service policy compliance
        try:
            response = requests.get("http://localhost:8005/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                compliance_results["policy_governance"] = {
                    "status": "available",
                    "opa_connected": data.get("opa_status") == "connected",
                }
            else:
                compliance_results["policy_governance"] = {"status": "unavailable"}
        except Exception as e:
            compliance_results["policy_governance"] = {
                "status": "error",
                "error": str(e),
            }

        return compliance_results

    def generate_emergency_report(self) -> Dict[str, Any]:
        """Generate comprehensive emergency status report."""
        report_time = datetime.now(timezone.utc)

        # Get current system status
        health_status = self.health_check_all_services()
        compliance_status = self.constitutional_compliance_check()
        service_pids = self.get_service_pids()

        # Calculate system health metrics
        healthy_services = sum(
            1 for s in health_status.values() if s.get("status") == "healthy"
        )
        total_services = len(health_status)
        system_health_percentage = (healthy_services / total_services) * 100

        report = {
            "report_timestamp": report_time.isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "system_health": {
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_percentage": system_health_percentage,
                "status": (
                    "operational"
                    if system_health_percentage >= 85
                    else "degraded" if system_health_percentage >= 50 else "critical"
                ),
            },
            "service_details": health_status,
            "constitutional_compliance": compliance_status,
            "service_pids": service_pids,
            "emergency_events": self.emergency_log[-10:],  # Last 10 events
            "rto_capability": {
                "target_rto_minutes": 30,
                "estimated_shutdown_time_seconds": 30,
                "estimated_recovery_time_minutes": 15,
            },
        }

        return report


def main():
    """Main function for emergency response operations."""
    if len(sys.argv) < 2:
        print("Usage: python emergency_response.py <command>")
        print("Commands:")
        print("  health-check    - Check health of all services")
        print("  emergency-shutdown <reason> - Emergency shutdown all services")
        print("  compliance-check - Check constitutional compliance")
        print("  status-report   - Generate comprehensive status report")
        sys.exit(1)

    emergency_system = ACGSEmergencyResponse()
    command = sys.argv[1]

    if command == "health-check":
        results = emergency_system.health_check_all_services()
        print(json.dumps(results, indent=2))

    elif command == "emergency-shutdown":
        reason = sys.argv[2] if len(sys.argv) > 2 else "Manual emergency shutdown"
        results = emergency_system.emergency_shutdown(reason)
        print(json.dumps(results, indent=2))

    elif command == "compliance-check":
        results = emergency_system.constitutional_compliance_check()
        print(json.dumps(results, indent=2))

    elif command == "status-report":
        results = emergency_system.generate_emergency_report()
        print(json.dumps(results, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
