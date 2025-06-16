#!/usr/bin/env python3
"""
ACGS-1 Emergency Rollback and Incident Response System
Provides automated rollback capabilities and emergency procedures
"""

import os
import sys
import json
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import psutil
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/dislove/ACGS-1/logs/emergency_procedures.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmergencyRollbackSystem:
    """Emergency rollback and incident response system for ACGS-1"""
    
    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.backup_root = Path("/home/dislove/ACGS-1/backups")
        self.services = [
            "auth_service", "ac_service", "integrity_service", 
            "fv_service", "gs_service", "pgc_service", "ec_service"
        ]
        self.service_ports = {
            "auth_service": 8000, "ac_service": 8001, "integrity_service": 8002,
            "fv_service": 8003, "gs_service": 8004, "pgc_service": 8005, "ec_service": 8006
        }
        self.emergency_contacts = {
            "primary": "ACGS-1 Operations Team",
            "secondary": "Infrastructure Team",
            "escalation": "System Architecture Team"
        }
        
    def emergency_stop_all_services(self) -> Dict:
        """Emergency stop all ACGS services"""
        logger.info("🚨 EMERGENCY: Stopping all ACGS services")
        
        try:
            stopped_services = []
            failed_services = []
            
            for service_name in self.services:
                port = self.service_ports[service_name]
                try:
                    # Kill processes on service ports
                    result = subprocess.run(
                        f"pkill -f 'uvicorn.*:{port}'", 
                        shell=True, 
                        capture_output=True, 
                        text=True
                    )
                    
                    # Verify service is stopped
                    time.sleep(2)
                    if not self._is_service_running(port):
                        stopped_services.append(service_name)
                        logger.info(f"✅ Stopped {service_name} on port {port}")
                    else:
                        # Force kill if still running
                        subprocess.run(f"fuser -k {port}/tcp", shell=True)
                        time.sleep(1)
                        if not self._is_service_running(port):
                            stopped_services.append(service_name)
                            logger.info(f"✅ Force stopped {service_name} on port {port}")
                        else:
                            failed_services.append(service_name)
                            logger.error(f"❌ Failed to stop {service_name} on port {port}")
                            
                except Exception as e:
                    failed_services.append(service_name)
                    logger.error(f"❌ Error stopping {service_name}: {e}")
            
            return {
                "status": "completed" if not failed_services else "partial",
                "stopped_services": stopped_services,
                "failed_services": failed_services,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Emergency stop failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def emergency_restart_services(self) -> Dict:
        """Emergency restart all ACGS services"""
        logger.info("🔄 EMERGENCY: Restarting all ACGS services")
        
        try:
            # First stop all services
            stop_result = self.emergency_stop_all_services()
            
            # Wait for clean shutdown
            time.sleep(10)
            
            # Start services using the startup script
            start_script = self.project_root / "scripts" / "start_missing_services.sh"
            if start_script.exists():
                result = subprocess.run(
                    ["bash", str(start_script)], 
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                # Wait for services to start
                time.sleep(30)
                
                # Verify services are running
                running_services = []
                failed_services = []
                
                for service_name in self.services:
                    port = self.service_ports[service_name]
                    if self._is_service_running(port):
                        running_services.append(service_name)
                    else:
                        failed_services.append(service_name)
                
                return {
                    "status": "completed" if not failed_services else "partial",
                    "running_services": running_services,
                    "failed_services": failed_services,
                    "stop_result": stop_result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"status": "failed", "error": "Start script not found"}
                
        except Exception as e:
            logger.error(f"❌ Emergency restart failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def isolate_service(self, service_name: str) -> Dict:
        """Isolate a specific service for troubleshooting"""
        logger.info(f"🔒 Isolating service: {service_name}")
        
        try:
            if service_name not in self.services:
                return {"status": "failed", "error": f"Unknown service: {service_name}"}
            
            port = self.service_ports[service_name]
            
            # Stop the specific service
            result = subprocess.run(
                f"pkill -f 'uvicorn.*:{port}'", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            # Verify service is stopped
            time.sleep(2)
            if not self._is_service_running(port):
                logger.info(f"✅ Service {service_name} isolated successfully")
                return {
                    "status": "success",
                    "service": service_name,
                    "port": port,
                    "isolated": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"status": "failed", "error": f"Failed to isolate {service_name}"}
                
        except Exception as e:
            logger.error(f"❌ Service isolation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def quick_health_check(self) -> Dict:
        """Quick health check for emergency assessment"""
        logger.info("🏥 Performing quick health check")
        
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "services": {},
                "overall_status": "unknown"
            }
            
            healthy_services = 0
            total_services = len(self.services)
            
            for service_name in self.services:
                port = self.service_ports[service_name]
                is_running = self._is_service_running(port)
                
                # Try to hit health endpoint
                health_endpoint_ok = False
                if is_running:
                    try:
                        response = requests.get(f"http://localhost:{port}/health", timeout=5)
                        health_endpoint_ok = response.status_code == 200
                    except:
                        health_endpoint_ok = False
                
                if is_running and health_endpoint_ok:
                    healthy_services += 1
                
                health_status["services"][service_name] = {
                    "running": is_running,
                    "health_endpoint": health_endpoint_ok,
                    "port": port
                }
            
            # Determine overall status
            if healthy_services == total_services:
                health_status["overall_status"] = "healthy"
            elif healthy_services > total_services / 2:
                health_status["overall_status"] = "degraded"
            else:
                health_status["overall_status"] = "critical"
            
            health_status["healthy_services"] = healthy_services
            health_status["total_services"] = total_services
            health_status["health_percentage"] = round((healthy_services / total_services) * 100, 1)
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def create_incident_report(self, incident_type: str, description: str, severity: str = "medium") -> Dict:
        """Create incident report"""
        logger.info(f"📋 Creating incident report: {incident_type}")
        
        try:
            incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            incident_report = {
                "incident_id": incident_id,
                "type": incident_type,
                "description": description,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
                "status": "open",
                "system_state": self.quick_health_check(),
                "emergency_contacts": self.emergency_contacts,
                "constitution_hash": "cdd01ef066bc6cf2"
            }
            
            # Save incident report
            incident_dir = self.project_root / "logs" / "incidents"
            incident_dir.mkdir(exist_ok=True)
            
            incident_file = incident_dir / f"{incident_id}.json"
            with open(incident_file, 'w') as f:
                json.dump(incident_report, f, indent=2)
            
            logger.info(f"✅ Incident report created: {incident_id}")
            return incident_report
            
        except Exception as e:
            logger.error(f"❌ Failed to create incident report: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _is_service_running(self, port: int) -> bool:
        """Check if service is running on given port"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except:
            return False
    
    def get_emergency_procedures(self) -> Dict:
        """Get emergency procedures documentation"""
        return {
            "emergency_contacts": self.emergency_contacts,
            "procedures": {
                "service_failure": {
                    "steps": [
                        "1. Run quick health check: python3 scripts/emergency_rollback_procedures.py health",
                        "2. Isolate failed service: python3 scripts/emergency_rollback_procedures.py isolate <service_name>",
                        "3. Check service logs: tail -f logs/<service_name>.log",
                        "4. Restart service: python3 scripts/emergency_rollback_procedures.py restart",
                        "5. Create incident report if needed"
                    ]
                },
                "system_wide_failure": {
                    "steps": [
                        "1. Emergency stop all services: python3 scripts/emergency_rollback_procedures.py stop",
                        "2. Create incident report: python3 scripts/emergency_rollback_procedures.py incident",
                        "3. Check system resources: htop, df -h",
                        "4. Restart services: python3 scripts/emergency_rollback_procedures.py restart",
                        "5. Verify system health: python3 scripts/comprehensive_health_check.py"
                    ]
                },
                "constitutional_compliance_failure": {
                    "steps": [
                        "1. Verify constitution hash: cdd01ef066bc6cf2",
                        "2. Check PGC service status",
                        "3. Validate blockchain connectivity",
                        "4. Restart governance services if needed",
                        "5. Contact constitutional governance team"
                    ]
                }
            },
            "escalation_matrix": {
                "low": "Log incident, monitor",
                "medium": "Contact primary on-call",
                "high": "Contact primary + secondary",
                "critical": "Contact all teams + escalation"
            }
        }


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-1 Emergency Rollback System")
    parser.add_argument("action", choices=["stop", "restart", "isolate", "health", "incident", "procedures"], 
                       help="Emergency action to perform")
    parser.add_argument("--service", help="Service name for isolation")
    parser.add_argument("--type", help="Incident type")
    parser.add_argument("--description", help="Incident description")
    parser.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium", 
                       help="Incident severity")
    
    args = parser.parse_args()
    
    # Ensure log directory exists
    log_dir = Path("/home/dislove/ACGS-1/logs")
    log_dir.mkdir(exist_ok=True)
    
    emergency_system = EmergencyRollbackSystem()
    
    if args.action == "stop":
        result = emergency_system.emergency_stop_all_services()
        print(json.dumps(result, indent=2))
        
    elif args.action == "restart":
        result = emergency_system.emergency_restart_services()
        print(json.dumps(result, indent=2))
        
    elif args.action == "isolate":
        if not args.service:
            print("Error: --service required for isolation")
            sys.exit(1)
        result = emergency_system.isolate_service(args.service)
        print(json.dumps(result, indent=2))
        
    elif args.action == "health":
        result = emergency_system.quick_health_check()
        print(json.dumps(result, indent=2))
        
    elif args.action == "incident":
        if not args.type or not args.description:
            print("Error: --type and --description required for incident report")
            sys.exit(1)
        result = emergency_system.create_incident_report(args.type, args.description, args.severity)
        print(json.dumps(result, indent=2))
        
    elif args.action == "procedures":
        result = emergency_system.get_emergency_procedures()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
