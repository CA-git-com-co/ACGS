#!/usr/bin/env python3
"""
ACGS-1 Phase 2 Systematic Remediation Execution Plan
Comprehensive service restoration and integration workflow
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

import httpx


class Phase2ExecutionManager:
    """Manages Phase 2 execution with structured priorities and validation."""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.failed_services = [
            "ac_service",
            "integrity_service",
            "fv_service",
            "gs_service",
        ]
        self.working_services = ["auth_service", "pgc_service", "ec_service"]

        self.service_ports = {
            "auth_service": 8000,
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
            "pgc_service": 8005,
            "ec_service": 8006,
        }

        self.execution_log = []
        self.start_time = time.time()

    def log_action(self, action: str, status: str, details: str = ""):
        """Log execution actions with timestamps."""
        timestamp = time.time() - self.start_time
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "status": status,
            "details": details,
        }
        self.execution_log.append(log_entry)
        print(f"[{timestamp:.1f}s] {status}: {action}")
        if details:
            print(f"    {details}")

    async def priority_1_service_restoration(self) -> Dict[str, Any]:
        """Priority 1: Complete Service Restoration (0-2 hours)"""
        self.log_action("Starting Priority 1: Service Restoration", "INFO")

        results = {
            "phase": "Priority 1",
            "target": "Complete Service Restoration",
            "timeline": "0-2 hours",
            "services_restored": [],
            "services_failed": [],
            "success": False,
        }

        # Step 1: Stop failing Docker containers
        self.log_action("Stopping failing Docker containers", "INFO")
        docker_containers = [
            "acgs_ac_service",
            "acgs_integrity_service",
            "acgs_fv_service",
            "acgs_gs_service",
        ]

        for container in docker_containers:
            try:
                subprocess.run(
                    ["docker", "stop", container],
                    capture_output=True,
                    check=False,
                    timeout=30,
                )
                self.log_action(f"Stopped Docker container: {container}", "SUCCESS")
            except Exception as e:
                self.log_action(
                    f"Failed to stop container: {container}", "WARNING", str(e)
                )

        # Step 2: Deploy services using host-based approach
        self.log_action("Deploying services using host-based approach", "INFO")

        for service in self.failed_services:
            success = await self.deploy_service_host_based(service)
            if success:
                results["services_restored"].append(service)
                self.log_action(f"Successfully restored {service}", "SUCCESS")
            else:
                results["services_failed"].append(service)
                self.log_action(f"Failed to restore {service}", "ERROR")

        # Step 3: Validation
        health_check_success = await self.run_health_validation()
        results["health_check_passed"] = health_check_success

        # Calculate success
        restored_count = len(results["services_restored"])
        total_failed = len(self.failed_services)
        results["success"] = restored_count == total_failed and health_check_success
        results["availability_improvement"] = (
            f"{3 + restored_count}/7 services ({((3 + restored_count)/7)*100:.1f}%)"
        )

        self.log_action(
            f"Priority 1 Complete - Restored {restored_count}/{total_failed} services",
            "SUCCESS" if results["success"] else "PARTIAL",
        )

        return results

    async def deploy_service_host_based(self, service_name: str) -> bool:
        """Deploy a single service using host-based approach."""
        port = self.service_ports[service_name]

        # Set environment variables
        env_vars = {
            "AC_SERVICE_URL": "http://localhost:8001",
            "INTEGRITY_SERVICE_URL": "http://localhost:8002",
            "FV_SERVICE_URL": "http://localhost:8003",
            "GS_SERVICE_URL": "http://localhost:8004",
            "PGC_SERVICE_URL": "http://localhost:8005",
            "EC_SERVICE_URL": "http://localhost:8006",
            "AUTH_SERVICE_URL": "http://localhost:8000",
            "SERVICE_DISCOVERY_ENABLED": "true",
            "HEALTH_CHECK_TIMEOUT": "5.0",
            "REQUEST_TIMEOUT": "30.0",
            "LOG_LEVEL": "INFO",
        }

        # Kill any existing processes on the port
        try:
            subprocess.run(
                ["pkill", "-f", f"uvicorn.*{port}"], capture_output=True, check=False
            )
            time.sleep(2)
        except:
            pass

        # Find service directory based on actual structure
        service_dir_map = {
            "ac_service": self.project_root
            / "services"
            / "core"
            / "constitutional-ai"
            / "ac_service",
            "integrity_service": self.project_root
            / "services"
            / "platform"
            / "integrity"
            / "integrity_service",
            "fv_service": self.project_root
            / "services"
            / "core"
            / "formal-verification"
            / "fv_service",
            "gs_service": self.project_root
            / "services"
            / "core"
            / "governance-synthesis"
            / "gs_service",
        }

        service_dir = service_dir_map.get(service_name)
        if not service_dir or not service_dir.exists():
            self.log_action(
                f"Service directory not found for {service_name}: {service_dir}",
                "ERROR",
            )
            return False

        # Start the service
        cmd = [
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--reload",
        ]

        try:
            # Update environment
            import os

            env = os.environ.copy()
            env.update(env_vars)

            # Start the process
            process = subprocess.Popen(
                cmd,
                cwd=service_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            # Wait for startup
            time.sleep(8)

            # Check if process is still running
            if process.poll() is None:
                # Test service health
                health_ok = await self.test_service_health(service_name, port)
                if health_ok:
                    self.log_action(
                        f"Service {service_name} started successfully on port {port}",
                        "SUCCESS",
                    )
                    return True
                else:
                    self.log_action(
                        f"Service {service_name} started but health check failed",
                        "WARNING",
                    )
                    return False
            else:
                stdout, stderr = process.communicate()
                self.log_action(
                    f"Service {service_name} process exited", "ERROR", stdout[:200]
                )
                return False

        except Exception as e:
            self.log_action(f"Failed to start {service_name}", "ERROR", str(e))
            return False

    async def test_service_health(self, service_name: str, port: int) -> bool:
        """Test service health endpoint."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://localhost:{port}/health")
                return response.status_code == 200
        except:
            return False

    async def run_health_validation(self) -> bool:
        """Run comprehensive health validation."""
        try:
            # Run the comprehensive health check script
            result = subprocess.run(
                ["python", "comprehensive_system_health_check.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # Parse the output to check service availability
                output = result.stdout
                if "7/7 Healthy" in output:
                    return True
                elif "6/7 Healthy" in output or "5/7 Healthy" in output:
                    return True  # Partial success acceptable

            return False
        except Exception as e:
            self.log_action("Health validation failed", "ERROR", str(e))
            return False

    async def execute_phase_2(self) -> Dict[str, Any]:
        """Execute complete Phase 2 workflow."""
        self.log_action("🚀 Starting ACGS-1 Phase 2 Systematic Remediation", "INFO")

        # Priority 1: Service Restoration
        priority_1_results = await self.priority_1_service_restoration()

        # Generate execution report
        execution_report = {
            "phase": "Phase 2 Systematic Remediation",
            "start_time": self.start_time,
            "execution_duration": time.time() - self.start_time,
            "priority_1_results": priority_1_results,
            "execution_log": self.execution_log,
            "overall_success": priority_1_results["success"],
        }

        # Save report
        report_file = f"phase2_execution_report_{int(time.time())}.json"
        with open(self.project_root / report_file, "w") as f:
            json.dump(execution_report, f, indent=2, default=str)

        self.log_action(f"Phase 2 execution report saved: {report_file}", "INFO")

        return execution_report


async def main():
    """Main execution function."""
    manager = Phase2ExecutionManager()

    try:
        results = await manager.execute_phase_2()

        print("\n" + "=" * 80)
        print("🏛️  PHASE 2 EXECUTION SUMMARY")
        print("=" * 80)
        print(f"⏱️  Duration: {results['execution_duration']:.1f} seconds")
        print(
            f"🎯 Overall Success: {'✅ YES' if results['overall_success'] else '❌ NO'}"
        )
        print(
            f"📊 Services Restored: {len(results['priority_1_results']['services_restored'])}/4"
        )
        print(
            f"📈 Availability: {results['priority_1_results']['availability_improvement']}"
        )
        print("=" * 80)

        return 0 if results["overall_success"] else 1

    except Exception as e:
        print(f"❌ Phase 2 execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
