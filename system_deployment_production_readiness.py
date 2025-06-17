#!/usr/bin/env python3
"""
ACGS-1 Production Readiness Validator
Validates system readiness for production deployment with comprehensive scoring.
"""

import json
import subprocess
import time

import requests


class ProductionReadinessValidator:
    def __init__(self):
        self.services = {
            "ac_service": "http://localhost:8001/health",
            "fv_service": "http://localhost:8013/health",
            "ec_service": "http://localhost:8006/health",
        }
        self.monitoring = {
            "prometheus": "http://localhost:9090/api/v1/query?query=up",
            "grafana": "http://localhost:3000/api/health",
        }
        self.scores = {}
        self.total_score = 0
        self.max_score = 100

    def check_service_health(self) -> tuple[int, dict]:
        """Check health of all core services."""
        print("🔍 Checking Service Health...")
        healthy_services = 0
        service_details = {}

        for service, url in self.services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        healthy_services += 1
                        service_details[service] = "healthy"
                        print(f"  ✅ {service}: healthy")
                    else:
                        service_details[service] = "degraded"
                        print(f"  ⚠️ {service}: degraded")
                else:
                    service_details[service] = "unhealthy"
                    print(f"  ❌ {service}: unhealthy")
            except Exception:
                service_details[service] = "unreachable"
                print(f"  ❌ {service}: unreachable")

        score = (healthy_services / len(self.services)) * 25
        self.scores["service_health"] = score
        return score, service_details

    def check_performance_metrics(self) -> tuple[int, dict]:
        """Check performance metrics and response times."""
        print("⚡ Checking Performance Metrics...")
        performance_data = {}

        # Test response times
        response_times = []
        for service, url in self.services.items():
            try:
                start_time = time.time()
                requests.get(url, timeout=5)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                performance_data[f"{service}_response_time"] = f"{response_time:.2f}ms"
                print(f"  📊 {service}: {response_time:.2f}ms")
            except Exception:
                response_times.append(5000)  # Penalty for failed requests
                performance_data[f"{service}_response_time"] = "timeout"

        avg_response_time = sum(response_times) / len(response_times)
        performance_data["average_response_time"] = f"{avg_response_time:.2f}ms"

        # Score based on response time (target <500ms)
        if avg_response_time < 50:
            score = 25
        elif avg_response_time < 100:
            score = 20
        elif avg_response_time < 500:
            score = 15
        else:
            score = 5

        self.scores["performance"] = score
        return score, performance_data

    def check_security_configuration(self) -> tuple[int, dict]:
        """Check security configuration and SSL setup."""
        print("🔒 Checking Security Configuration...")
        security_data = {}
        score = 0

        # Check SSL certificate
        try:
            result = subprocess.run(
                [
                    "openssl",
                    "x509",
                    "-in",
                    "ssl/certs/acgs-services.crt",
                    "-text",
                    "-noout",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "Validity" in result.stdout:
                security_data["ssl_certificate"] = "valid"
                score += 10
                print("  ✅ SSL certificate: valid")
            else:
                security_data["ssl_certificate"] = "invalid"
                print("  ❌ SSL certificate: invalid")
        except Exception:
            security_data["ssl_certificate"] = "not_found"
            print("  ❌ SSL certificate: not found")

        # Check HTTPS configuration
        try:
            requests.get("https://localhost:8443/", verify=False, timeout=5)
            security_data["https_enabled"] = "yes"
            score += 10
            print("  ✅ HTTPS: enabled")
        except Exception:
            security_data["https_enabled"] = "no"
            print("  ⚠️ HTTPS: not accessible")

        # Check container security
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if result.returncode == 0:
                container_count = len(
                    [line for line in result.stdout.split("\n") if "acgs" in line]
                )
                security_data["containers_running"] = container_count
                if container_count >= 3:
                    score += 5
                    print(f"  ✅ Containers: {container_count} running")
                else:
                    print(f"  ⚠️ Containers: only {container_count} running")
        except Exception:
            security_data["containers_running"] = 0
            print("  ❌ Container check failed")

        self.scores["security"] = score
        return score, security_data

    def check_monitoring_infrastructure(self) -> tuple[int, dict]:
        """Check monitoring and alerting infrastructure."""
        print("📊 Checking Monitoring Infrastructure...")
        monitoring_data = {}
        score = 0

        for service, url in self.monitoring.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    monitoring_data[service] = "operational"
                    score += 12.5
                    print(f"  ✅ {service}: operational")
                else:
                    monitoring_data[service] = "degraded"
                    print(f"  ⚠️ {service}: degraded")
            except Exception:
                monitoring_data[service] = "unreachable"
                print(f"  ❌ {service}: unreachable")

        self.scores["monitoring"] = score
        return score, monitoring_data

    def generate_readiness_report(self) -> dict:
        """Generate comprehensive readiness report."""
        print("\n" + "=" * 60)
        print("🚀 ACGS-1 PRODUCTION READINESS VALIDATION")
        print("=" * 60)

        # Run all checks
        service_score, service_data = self.check_service_health()
        performance_score, performance_data = self.check_performance_metrics()
        security_score, security_data = self.check_security_configuration()
        monitoring_score, monitoring_data = self.check_monitoring_infrastructure()

        self.total_score = (
            service_score + performance_score + security_score + monitoring_score
        )

        # Generate report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_score": self.total_score,
            "max_score": self.max_score,
            "readiness_percentage": (self.total_score / self.max_score) * 100,
            "category_scores": self.scores,
            "service_health": service_data,
            "performance_metrics": performance_data,
            "security_configuration": security_data,
            "monitoring_infrastructure": monitoring_data,
        }

        return report

    def print_summary(self, report: dict):
        """Print readiness summary."""
        print("\n📋 PRODUCTION READINESS SUMMARY")
        print("-" * 40)
        print(
            f"Overall Score: {report['total_score']:.1f}/{report['max_score']} ({report['readiness_percentage']:.1f}%)"
        )
        print(f"Service Health: {self.scores.get('service_health', 0):.1f}/25")
        print(f"Performance: {self.scores.get('performance', 0):.1f}/25")
        print(f"Security: {self.scores.get('security', 0):.1f}/25")
        print(f"Monitoring: {self.scores.get('monitoring', 0):.1f}/25")

        if report["readiness_percentage"] >= 90:
            print("\n🎉 PRODUCTION READY - Deployment approved!")
        elif report["readiness_percentage"] >= 75:
            print("\n⚠️ MOSTLY READY - Minor issues to address")
        else:
            print("\n🚨 NOT READY - Critical issues must be resolved")


def main():
    validator = ProductionReadinessValidator()
    report = validator.generate_readiness_report()
    validator.print_summary(report)

    # Save report
    with open("production_readiness_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📄 Detailed report saved to: production_readiness_report.json")

    return 0 if report["readiness_percentage"] >= 90 else 1


if __name__ == "__main__":
    exit(main())
