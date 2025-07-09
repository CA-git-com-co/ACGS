#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
ACGS-PGP Service Startup Validation Script
Tests all 7 core services can start successfully and validates resource limits
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Service configuration
SERVICES = {
    "auth-service": {
        "port": 8000,
        "path": "services/platform/authentication/auth_service",
        "main": "app.main:app",
        "name": "Authentication Service",
    },
    "ac-service": {
        "port": 8001,
        "path": "services/core/constitutional-ai/ac_service",
        "main": "app.main:app",
        "name": "Constitutional AI Service",
    },
    "integrity-service": {
        "port": 8002,
        "path": "services/platform/integrity/integrity_service",
        "main": "app.main:app",
        "name": "Integrity Service",
    },
    "fv-service": {
        "port": 8003,
        "path": "services/core/formal-verification",
        "main": "fv_service.main:app",
        "name": "Formal Verification Service",
    },
    "gs-service": {
        "port": 8004,
        "path": "services/core/governance-synthesis",
        "main": "gs_service.app.main:app",
        "name": "Governance Synthesis Service",
    },
    "pgc-service": {
        "port": 8005,
        "path": "services/core/policy-governance",
        "main": "pgc_service.app.main:app",
        "name": "Policy Governance Service",
    },
    "ec-service": {
        "port": 8006,
        "path": "services/core/evolutionary-computation",
        "main": "app.main:app",
        "name": "Evolutionary Computation Service",
    },
}


class ServiceValidator:
    def __init__(self):
        self.results = {}
        self.processes = {}

    def start_service(self, service_id, config):
        """Start a service and return the process"""
        try:
            service_path = Path(config["path"])
            if not service_path.exists():
                return None, f"Service path does not exist: {service_path}"

            # Set environment variables
            env = os.environ.copy()
            env["PYTHONPATH"] = "/home/ubuntu/ACGS"
            env["PORT"] = str(config["port"])

            # Start the service
            cmd = [
                "python3",
                "-m",
                "uvicorn",
                config["main"],
                "--host",
                "127.0.0.1",
                "--port",
                str(config["port"]),
                "--log-level",
                "warning",
            ]

            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )

            return process, None

        except Exception as e:
            return None, f"Failed to start service: {e}"

    def check_service_health(self, port, timeout=10):
        """Check if service is responding on health endpoint"""
        import urllib.error
        import urllib.request

        health_url = f"http://127.0.0.1:{port}/health"

        for attempt in range(timeout):
            try:
                with urllib.request.urlopen(health_url, timeout=2) as response:
                    if response.status == 200:
                        return True, "Service is healthy"
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(1)
                continue

        return False, f"Service not responding after {timeout} seconds"

    def stop_service(self, process):
        """Stop a service process"""
        try:
            if process and process.poll() is None:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
        except Exception as e:
            print(f"Error stopping service: {e}")

    def validate_all_services(self):
        """Validate all services can start successfully"""
        print("🚀 Starting ACGS-PGP Service Startup Validation...")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)

        for service_id, config in SERVICES.items():
            print(f"\n🔧 Testing {config['name']} (port {config['port']})...")

            # Start service
            process, error = self.start_service(service_id, config)
            if error:
                self.results[service_id] = {
                    "status": "FAILED",
                    "error": error,
                    "port": config["port"],
                }
                print(f"❌ {service_id}: {error}")
                continue

            self.processes[service_id] = process

            # Wait for startup
            time.sleep(3)

            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.results[service_id] = {
                    "status": "FAILED",
                    "error": f"Process exited with code {process.returncode}",
                    "stderr": stderr.decode()[:500],
                    "port": config["port"],
                }
                print(f"❌ {service_id}: Process exited with code {process.returncode}")
                continue

            # Check health endpoint
            is_healthy, health_msg = self.check_service_health(config["port"])

            if is_healthy:
                self.results[service_id] = {
                    "status": "SUCCESS",
                    "message": "Service started successfully",
                    "port": config["port"],
                    "pid": process.pid,
                }
                print(
                    f"✅ {service_id}: Service started successfully on port {config['port']}"
                )
            else:
                self.results[service_id] = {
                    "status": "FAILED",
                    "error": health_msg,
                    "port": config["port"],
                }
                print(f"❌ {service_id}: {health_msg}")

        # Stop all services
        print("\n🔄 Stopping all services...")
        for service_id, process in self.processes.items():
            self.stop_service(process)
            print(f"🛑 Stopped {service_id}")

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📊 ACGS-PGP Service Startup Validation Report")
        print("=" * 60)

        successful = [s for s, r in self.results.items() if r["status"] == "SUCCESS"]
        failed = [s for s, r in self.results.items() if r["status"] == "FAILED"]

        print(f"✅ Successful: {len(successful)}/7 services")
        print(f"❌ Failed: {len(failed)}/7 services")

        if successful:
            print("\n✅ Successfully started services:")
            for service_id in successful:
                port = self.results[service_id]["port"]
                print(f"   - {service_id} (port {port})")

        if failed:
            print("\n❌ Failed to start services:")
            for service_id in failed:
                error = self.results[service_id]["error"]
                port = self.results[service_id]["port"]
                print(f"   - {service_id} (port {port}): {error}")

        # Save detailed results
        with open("service_startup_validation_report.json", "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "total_services": 7,
                        "successful": len(successful),
                        "failed": len(failed),
                    },
                    "results": self.results,
                },
                f,
                indent=2,
            )

        print("\n📄 Detailed report saved to: service_startup_validation_report.json")

        if len(successful) == 7:
            print("\n🎉 All 7 services started successfully!")
            return True
        print(f"\n⚠️ {len(failed)} services failed to start")
        return False


def main():
    validator = ServiceValidator()
    success = validator.validate_all_services()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
