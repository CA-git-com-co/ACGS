#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
ACGS-PGP Metrics Endpoint Analysis Script
Analyzes all 7 core services to identify metrics endpoints returning JSON fallback format
"""

import json
import subprocess
import sys
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


class MetricsAnalyzer:
    def __init__(self):
        self.results = {}
        self.processes = {}

    def start_service(self, service_id, config):
        """Start a service for metrics analysis"""
        try:
            service_path = Path(config["path"])
            if not service_path.exists():
                return None, f"Service path does not exist: {service_path}"

            # Set environment variables
            env = {"PYTHONPATH": "/home/ubuntu/ACGS", "PORT": str(config["port"])}

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
                "error",
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

    def check_metrics_endpoint(self, port, timeout=5):
        """Check metrics endpoint format"""
        import urllib.error
        import urllib.request

        metrics_url = f"http://127.0.0.1:{port}/metrics"

        try:
            with urllib.request.urlopen(metrics_url, timeout=timeout) as response:
                content = response.read().decode()
                content_type = response.headers.get("content-type", "")

                # Check if it's JSON format (fallback)
                if "application/json" in content_type:
                    try:
                        json_data = json.loads(content)
                        return {
                            "status": "JSON_FALLBACK",
                            "content_type": content_type,
                            "format": "JSON",
                            "sample": (
                                str(json_data)[:200] + "..."
                                if len(str(json_data)) > 200
                                else str(json_data)
                            ),
                        }
                    except json.JSONDecodeError:
                        pass

                # Check if it's Prometheus format
                if "text/plain" in content_type or content.startswith("#"):
                    return {
                        "status": "PROMETHEUS_FORMAT",
                        "content_type": content_type,
                        "format": "Prometheus",
                        "sample": (
                            content[:200] + "..." if len(content) > 200 else content
                        ),
                    }

                # Unknown format
                return {
                    "status": "UNKNOWN_FORMAT",
                    "content_type": content_type,
                    "format": "Unknown",
                    "sample": content[:200] + "..." if len(content) > 200 else content,
                }

        except urllib.error.HTTPError as e:
            return {
                "status": "HTTP_ERROR",
                "error": f"HTTP {e.code}: {e.reason}",
                "format": "Error",
            }
        except Exception as e:
            return {"status": "CONNECTION_ERROR", "error": str(e), "format": "Error"}

    def analyze_all_metrics(self):
        """Analyze metrics endpoints for all services"""
        print("🔍 Starting ACGS-PGP Metrics Endpoint Analysis...")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print("=" * 70)

        # Check metrics endpoints without starting services (if already running)
        for service_id, config in SERVICES.items():
            print(f"\n📊 Analyzing {config['name']} metrics (port {config['port']})...")

            metrics_result = self.check_metrics_endpoint(config["port"])

            self.results[service_id] = {
                "service_name": config["name"],
                "port": config["port"],
                "metrics_analysis": metrics_result,
            }

            if metrics_result["status"] == "JSON_FALLBACK":
                print(f"❌ {service_id}: JSON fallback format detected")
                print(f"   Content-Type: {metrics_result['content_type']}")
                print(f"   Sample: {metrics_result['sample'][:100]}...")
            elif metrics_result["status"] == "PROMETHEUS_FORMAT":
                print(f"✅ {service_id}: Proper Prometheus format")
                print(f"   Content-Type: {metrics_result['content_type']}")
            elif metrics_result["status"] == "CONNECTION_ERROR":
                print(
                    f"⚠️ {service_id}: Service not running - {metrics_result['error']}"
                )
            else:
                print(
                    f"❓ {service_id}: {metrics_result['status']} - {metrics_result.get('error', 'Unknown format')}"
                )

        # Generate report
        self.generate_metrics_report()

    def generate_metrics_report(self):
        """Generate metrics analysis report"""
        print("\n" + "=" * 70)
        print("📊 ACGS-PGP Metrics Endpoint Analysis Report")
        print("=" * 70)

        json_fallback = []
        prometheus_format = []
        errors = []

        for service_id, result in self.results.items():
            status = result["metrics_analysis"]["status"]
            if status == "JSON_FALLBACK":
                json_fallback.append(service_id)
            elif status == "PROMETHEUS_FORMAT":
                prometheus_format.append(service_id)
            else:
                errors.append(service_id)

        print(f"✅ Prometheus Format: {len(prometheus_format)}/7 services")
        print(f"❌ JSON Fallback: {len(json_fallback)}/7 services")
        print(f"⚠️ Errors/Not Running: {len(errors)}/7 services")

        if prometheus_format:
            print("\n✅ Services with proper Prometheus format:")
            for service_id in prometheus_format:
                port = self.results[service_id]["port"]
                print(f"   - {service_id} (port {port})")

        if json_fallback:
            print("\n❌ Services with JSON fallback format (NEED FIXING):")
            for service_id in json_fallback:
                port = self.results[service_id]["port"]
                print(f"   - {service_id} (port {port})")

        if errors:
            print("\n⚠️ Services with errors or not running:")
            for service_id in errors:
                port = self.results[service_id]["port"]
                error = self.results[service_id]["metrics_analysis"].get(
                    "error", "Unknown error"
                )
                print(f"   - {service_id} (port {port}): {error}")

        # Save detailed results
        with open("metrics_analysis_report.json", "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "total_services": 7,
                        "prometheus_format": len(prometheus_format),
                        "json_fallback": len(json_fallback),
                        "errors": len(errors),
                    },
                    "results": self.results,
                },
                f,
                indent=2,
            )

        print("\n📄 Detailed report saved to: metrics_analysis_report.json")

        if len(json_fallback) > 0:
            print(
                f"\n🔧 Next Steps: Convert {len(json_fallback)} services from JSON to Prometheus format"
            )
            return False
        print("\n🎉 All services are using proper Prometheus format!")
        return True


def main():
    analyzer = MetricsAnalyzer()
    success = analyzer.analyze_all_metrics()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
