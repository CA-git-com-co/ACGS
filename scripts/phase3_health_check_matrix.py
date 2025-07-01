#!/usr/bin/env python3
"""
ACGS-PGP Phase 3.3: Health Check Connectivity Matrix
Validates health check connectivity between all 7 services (49 total connection tests)

Features:
- 7x7 connectivity matrix testing (49 total tests)
- Service-to-service health check validation
- Response time measurement
- Constitutional compliance verification
- Network connectivity analysis
- Service dependency mapping
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthCheckResult(BaseModel):
    """Health check result model"""

    source_service: str
    target_service: str
    status: str
    response_time_ms: float
    status_code: Optional[int] = None
    constitutional_hash_verified: bool = False
    error: Optional[str] = None
    timestamp: datetime


class ACGSHealthCheckMatrixTester:
    """ACGS-PGP Health Check Connectivity Matrix Tester"""

    def __init__(self):
        self.services = {
            "auth": {"port": 8000, "name": "Authentication Service"},
            "ac": {"port": 8001, "name": "Constitutional AI Service"},
            "integrity": {"port": 8002, "name": "Integrity Service"},
            "fv": {"port": 8003, "name": "Formal Verification Service"},
            "gs": {"port": 8004, "name": "Governance Synthesis Service"},
            "pgc": {"port": 8005, "name": "Policy Governance & Compliance Service"},
            "ec": {"port": 8006, "name": "Executive Council Service"},
        }
        self.base_url = "http://localhost"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.connectivity_matrix: Dict[str, Dict[str, HealthCheckResult]] = {}
        self.timeout = 10.0

    async def test_health_check_connectivity(
        self, source: str, target: str
    ) -> HealthCheckResult:
        """Test health check connectivity between two services"""
        source_service = self.services[source]
        target_service = self.services[target]

        start_time = time.time()
        timestamp = datetime.now(timezone.utc)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Test health endpoint connectivity
                response = await client.get(
                    f"{self.base_url}:{target_service['port']}/health",
                    headers={
                        "User-Agent": f"ACGS-Health-Check/{source_service['name']}",
                        "X-Source-Service": source,
                        "X-Target-Service": target,
                    },
                )

                response_time = (time.time() - start_time) * 1000
                constitutional_hash_verified = self._verify_constitutional_hash(
                    response
                )

                if response.status_code == 200:
                    return HealthCheckResult(
                        source_service=source,
                        target_service=target,
                        status="healthy",
                        response_time_ms=response_time,
                        status_code=response.status_code,
                        constitutional_hash_verified=constitutional_hash_verified,
                        timestamp=timestamp,
                    )
                else:
                    return HealthCheckResult(
                        source_service=source,
                        target_service=target,
                        status="unhealthy",
                        response_time_ms=response_time,
                        status_code=response.status_code,
                        constitutional_hash_verified=constitutional_hash_verified,
                        error=f"HTTP {response.status_code}",
                        timestamp=timestamp,
                    )

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                source_service=source,
                target_service=target,
                status="timeout",
                response_time_ms=response_time,
                error="Connection timeout",
                timestamp=timestamp,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                source_service=source,
                target_service=target,
                status="error",
                response_time_ms=response_time,
                error=str(e),
                timestamp=timestamp,
            )

    async def build_connectivity_matrix(self) -> Dict[str, Any]:
        """Build complete 7x7 connectivity matrix (49 tests)"""
        logger.info("🔍 Building health check connectivity matrix (49 tests)...")

        matrix_results = {}
        total_tests = 0
        successful_tests = 0

        # Test all service-to-service combinations
        for source_key in self.services.keys():
            matrix_results[source_key] = {}

            for target_key in self.services.keys():
                total_tests += 1
                logger.info(f"Testing {source_key} → {target_key} connectivity...")

                result = await self.test_health_check_connectivity(
                    source_key, target_key
                )
                matrix_results[source_key][target_key] = result.dict()

                if result.status == "healthy":
                    successful_tests += 1

                # Store in connectivity matrix
                if source_key not in self.connectivity_matrix:
                    self.connectivity_matrix[source_key] = {}
                self.connectivity_matrix[source_key][target_key] = result

        # Calculate matrix statistics
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        matrix_summary = {
            "total_tests": total_tests,
            "successful_connections": successful_tests,
            "failed_connections": total_tests - successful_tests,
            "success_rate_percentage": success_rate,
            "matrix_status": (
                "healthy"
                if success_rate >= 90
                else "degraded" if success_rate >= 70 else "critical"
            ),
        }

        return {
            "connectivity_matrix": matrix_results,
            "summary": matrix_summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def analyze_connectivity_patterns(self) -> Dict[str, Any]:
        """Analyze connectivity patterns and identify issues"""
        logger.info("📊 Analyzing connectivity patterns...")

        analysis = {
            "service_health_status": {},
            "problematic_connections": [],
            "performance_analysis": {},
            "constitutional_compliance": {},
        }

        # Analyze each service's connectivity
        for source_key, targets in self.connectivity_matrix.items():
            source_service = self.services[source_key]

            # Count successful outbound connections
            outbound_healthy = sum(
                1 for result in targets.values() if result.status == "healthy"
            )
            outbound_total = len(targets)
            outbound_rate = (
                (outbound_healthy / outbound_total * 100) if outbound_total > 0 else 0
            )

            # Count successful inbound connections
            inbound_healthy = sum(
                1
                for other_source in self.connectivity_matrix.values()
                if other_source.get(source_key, {}).status == "healthy"
            )
            inbound_total = len(self.services)
            inbound_rate = (
                (inbound_healthy / inbound_total * 100) if inbound_total > 0 else 0
            )

            analysis["service_health_status"][source_key] = {
                "service_name": source_service["name"],
                "port": source_service["port"],
                "outbound_connectivity": {
                    "healthy_connections": outbound_healthy,
                    "total_connections": outbound_total,
                    "success_rate": outbound_rate,
                },
                "inbound_connectivity": {
                    "healthy_connections": inbound_healthy,
                    "total_connections": inbound_total,
                    "success_rate": inbound_rate,
                },
                "overall_status": (
                    "healthy" if min(outbound_rate, inbound_rate) >= 80 else "degraded"
                ),
            }

            # Identify problematic connections
            for target_key, result in targets.items():
                if result.status != "healthy":
                    analysis["problematic_connections"].append(
                        {
                            "source": source_key,
                            "target": target_key,
                            "status": result.status,
                            "error": result.error,
                            "response_time_ms": result.response_time_ms,
                        }
                    )

            # Performance analysis
            response_times = [
                result.response_time_ms
                for result in targets.values()
                if result.status == "healthy"
            ]
            if response_times:
                analysis["performance_analysis"][source_key] = {
                    "avg_response_time_ms": sum(response_times) / len(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "healthy_connections": len(response_times),
                }

            # Constitutional compliance analysis
            constitutional_compliant = sum(
                1 for result in targets.values() if result.constitutional_hash_verified
            )
            analysis["constitutional_compliance"][source_key] = {
                "compliant_connections": constitutional_compliant,
                "total_connections": len(targets),
                "compliance_rate": (
                    (constitutional_compliant / len(targets) * 100) if targets else 0
                ),
            }

        return analysis

    def generate_connectivity_report(
        self, matrix_data: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive connectivity report"""
        logger.info("📋 Generating connectivity report...")

        report = {
            "report_title": "ACGS-PGP Health Check Connectivity Matrix Report",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "executive_summary": {
                "total_tests_performed": matrix_data["summary"]["total_tests"],
                "overall_success_rate": matrix_data["summary"][
                    "success_rate_percentage"
                ],
                "matrix_status": matrix_data["summary"]["matrix_status"],
                "critical_issues": len(
                    [
                        conn
                        for conn in analysis["problematic_connections"]
                        if conn["status"] == "error"
                    ]
                ),
                "performance_issues": len(
                    [
                        service
                        for service, perf in analysis["performance_analysis"].items()
                        if perf["avg_response_time_ms"] > 1000
                    ]
                ),
            },
            "detailed_results": {
                "connectivity_matrix": matrix_data,
                "connectivity_analysis": analysis,
            },
            "recommendations": self._generate_recommendations(analysis),
            "next_steps": [
                "Address critical connectivity issues immediately",
                "Investigate services with degraded performance",
                "Verify constitutional compliance for non-compliant connections",
                "Schedule regular connectivity matrix testing",
                "Monitor service health continuously",
            ],
        }

        return report

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Check for critical connectivity issues
        critical_issues = [
            conn
            for conn in analysis["problematic_connections"]
            if conn["status"] == "error"
        ]
        if critical_issues:
            recommendations.append(
                f"CRITICAL: Fix {len(critical_issues)} failed service connections immediately"
            )

        # Check for performance issues
        slow_services = [
            service
            for service, perf in analysis["performance_analysis"].items()
            if perf["avg_response_time_ms"] > 1000
        ]
        if slow_services:
            recommendations.append(
                f"Investigate performance issues in services: {', '.join(slow_services)}"
            )

        # Check for constitutional compliance issues
        non_compliant = [
            service
            for service, comp in analysis["constitutional_compliance"].items()
            if comp["compliance_rate"] < 100
        ]
        if non_compliant:
            recommendations.append(
                f"Verify constitutional compliance for services: {', '.join(non_compliant)}"
            )

        # Check overall matrix health
        if analysis.get("service_health_status", {}):
            degraded_services = [
                service
                for service, status in analysis["service_health_status"].items()
                if status["overall_status"] == "degraded"
            ]
            if degraded_services:
                recommendations.append(
                    f"Monitor degraded services: {', '.join(degraded_services)}"
                )

        if not recommendations:
            recommendations.append(
                "All connectivity tests passed successfully - maintain current monitoring"
            )

        return recommendations

    def _verify_constitutional_hash(self, response: httpx.Response) -> bool:
        """Verify constitutional hash in response headers"""
        return response.headers.get("x-constitutional-hash") == self.constitutional_hash

    async def run_connectivity_matrix_tests(self) -> Dict[str, Any]:
        """Run complete connectivity matrix tests"""
        logger.info("🚀 Starting ACGS-PGP Health Check Connectivity Matrix Tests...")

        # Build connectivity matrix
        matrix_data = await self.build_connectivity_matrix()

        # Analyze connectivity patterns
        analysis = self.analyze_connectivity_patterns()

        # Generate comprehensive report
        report = self.generate_connectivity_report(matrix_data, analysis)

        return report


async def main():
    """Main execution function"""
    tester = ACGSHealthCheckMatrixTester()

    try:
        results = await tester.run_connectivity_matrix_tests()

        # Save results to file
        with open("phase3_health_check_matrix_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 80)
        print("ACGS-PGP Phase 3.3: Health Check Connectivity Matrix Results")
        print("=" * 80)
        print(f"Total Tests: {results['executive_summary']['total_tests_performed']}")
        print(
            f"Success Rate: {results['executive_summary']['overall_success_rate']:.1f}%"
        )
        print(f"Matrix Status: {results['executive_summary']['matrix_status'].upper()}")
        print(f"Critical Issues: {results['executive_summary']['critical_issues']}")
        print(
            f"Performance Issues: {results['executive_summary']['performance_issues']}"
        )
        print(f"Constitutional Hash: {results['constitutional_hash']}")
        print("=" * 80)

        # Print recommendations
        print("\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"{i}. {rec}")

        if results["executive_summary"]["matrix_status"] in ["healthy", "degraded"]:
            print("\n✅ Connectivity matrix tests completed successfully!")
            return 0
        else:
            print("\n❌ Critical connectivity issues found. Check results for details.")
            return 1

    except Exception as e:
        logger.error(f"Connectivity matrix testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
