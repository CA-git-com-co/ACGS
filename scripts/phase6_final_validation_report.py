#!/usr/bin/env python3
"""
ACGS-PGP Phase 6: Final Validation & Comprehensive Reporting
Consolidates all test results and generates comprehensive system validation report

Features:
- Consolidates results from all 5 previous phases
- Generates executive summary with key metrics
- Provides operational readiness assessment
- Creates remediation recommendations
- Validates against ACGS-PGP requirements
- Generates final system health report
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemValidationReport(BaseModel):
    """System validation report model"""

    report_title: str
    timestamp: datetime
    constitutional_hash: str
    overall_status: str
    system_health_score: float
    operational_readiness: str
    phase_results: Dict[str, Any]
    executive_summary: Dict[str, Any]
    recommendations: List[str]
    next_steps: List[str]


class ACGSFinalValidator:
    """ACGS-PGP Final Validation & Reporting System"""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.required_services = ["ac", "integrity", "fv", "ec"]
        self.target_metrics = {
            "response_time_ms": 2000,
            "availability_percentage": 99.9,
            "constitutional_compliance": 95.0,
            "concurrent_requests": 20,
            "emergency_rto_seconds": 1800,
        }

    def load_phase_results(self) -> Dict[str, Any]:
        """Load results from all testing phases"""
        logger.info("📊 Loading results from all testing phases...")

        phase_files = {
            "phase1": "phase1_security_scan_results.json",
            "phase2": "phase2_dependency_audit_results.json",
            "phase3_integration": "phase3_integration_test_results.json",
            "phase3_authentication": "phase3_authentication_test_results.json",
            "phase3_health_matrix": "phase3_health_check_matrix_results.json",
            "phase4": "phase4_constitutional_compliance_results.json",
            "phase5": "phase5_performance_validation_results.json",
        }

        phase_results = {}

        for phase_name, filename in phase_files.items():
            try:
                if os.path.exists(filename):
                    with open(filename, "r") as f:
                        phase_results[phase_name] = json.load(f)
                    logger.info(f"✅ Loaded {phase_name} results from {filename}")
                else:
                    logger.warning(f"⚠️ File not found: {filename}")
                    phase_results[phase_name] = {
                        "status": "not_found",
                        "error": f"File {filename} not found",
                    }
            except Exception as e:
                logger.error(f"❌ Error loading {filename}: {e}")
                phase_results[phase_name] = {"status": "error", "error": str(e)}

        return phase_results

    def calculate_system_health_score(self, phase_results: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)"""
        logger.info("🏥 Calculating system health score...")

        scores = []
        weights = {
            "phase1": 0.15,  # Security scanning
            "phase2": 0.10,  # Dependency audit
            "phase3_integration": 0.20,  # Service integration
            "phase3_authentication": 0.15,  # Authentication
            "phase3_health_matrix": 0.15,  # Health connectivity
            "phase4": 0.15,  # Constitutional compliance
            "phase5": 0.10,  # Performance validation
        }

        for phase_name, weight in weights.items():
            phase_data = phase_results.get(phase_name, {})

            # Calculate phase score based on status and metrics
            if phase_data.get("status") == "not_found":
                phase_score = 0
            elif phase_data.get("overall_status") == "passed":
                phase_score = 100
            elif phase_data.get("overall_status") == "failed":
                # Check for partial success
                summary = phase_data.get("summary", {})
                if "success_rate" in summary:
                    phase_score = summary["success_rate"]
                elif "passed_tests" in summary and "total_tests" in summary:
                    phase_score = (
                        summary["passed_tests"] / summary["total_tests"]
                    ) * 100
                else:
                    phase_score = 30  # Partial credit for attempted tests
            else:
                # Try to extract success metrics
                if "executive_summary" in phase_data:
                    exec_summary = phase_data["executive_summary"]
                    if "overall_success_rate" in exec_summary:
                        phase_score = exec_summary["overall_success_rate"]
                    else:
                        phase_score = 50  # Default for unclear status
                else:
                    phase_score = 50

            weighted_score = phase_score * weight
            scores.append(weighted_score)
            logger.info(
                f"Phase {phase_name}: {phase_score:.1f}% (weight: {weight:.2f}, contribution: {weighted_score:.1f})"
            )

        total_score = sum(scores)
        logger.info(f"Overall system health score: {total_score:.1f}%")
        return total_score

    def assess_operational_readiness(
        self, health_score: float, phase_results: Dict[str, Any]
    ) -> str:
        """Assess operational readiness based on health score and critical metrics"""
        logger.info("🚀 Assessing operational readiness...")

        # Check critical requirements
        critical_checks = {
            "services_running": False,
            "constitutional_compliance": False,
            "performance_acceptable": False,
            "security_baseline": False,
        }

        # Check if services are running (from health matrix)
        health_matrix = phase_results.get("phase3_health_matrix", {})
        if (
            health_matrix.get("executive_summary", {}).get("overall_success_rate", 0)
            >= 70
        ):
            critical_checks["services_running"] = True

        # Check constitutional compliance
        constitutional = phase_results.get("phase4", {})
        if constitutional.get("overall_status") == "passed":
            critical_checks["constitutional_compliance"] = True

        # Check performance
        performance = phase_results.get("phase5", {})
        if performance.get("overall_status") == "passed":
            critical_checks["performance_acceptable"] = True

        # Check security baseline
        security = phase_results.get("phase1", {})
        if security.get("status") != "error":
            critical_checks["security_baseline"] = True

        critical_passed = sum(critical_checks.values())
        total_critical = len(critical_checks)

        logger.info(f"Critical checks passed: {critical_passed}/{total_critical}")

        if health_score >= 85 and critical_passed >= 3:
            return "production_ready"
        elif health_score >= 70 and critical_passed >= 2:
            return "staging_ready"
        elif health_score >= 50:
            return "development_ready"
        else:
            return "needs_remediation"

    def generate_executive_summary(
        self,
        phase_results: Dict[str, Any],
        health_score: float,
        operational_readiness: str,
    ) -> Dict[str, Any]:
        """Generate executive summary with key metrics"""
        logger.info("📋 Generating executive summary...")

        # Count services and their status
        health_matrix = phase_results.get("phase3_health_matrix", {})
        services_status = (
            health_matrix.get("detailed_results", {})
            .get("connectivity_analysis", {})
            .get("service_health_status", {})
        )

        healthy_services = sum(
            1
            for service in services_status.values()
            if service.get("overall_status") == "healthy"
        )
        total_services = len(services_status)

        # Performance metrics
        performance = phase_results.get("phase5", {})
        avg_response_time = 0
        if (
            performance.get("results", {})
            .get("response_time_compliance", {})
            .get("service_results")
        ):
            response_times = [
                service.get("response_time_ms", 0)
                for service in performance["results"]["response_time_compliance"][
                    "service_results"
                ].values()
            ]
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

        # Constitutional compliance
        constitutional = phase_results.get("phase4", {})
        constitutional_score = 0
        if constitutional.get("results", {}).get("constitutional_hash_consistency"):
            constitutional_score = constitutional["results"][
                "constitutional_hash_consistency"
            ].get("consistency_rate", 0)

        return {
            "system_health_score": health_score,
            "operational_readiness": operational_readiness,
            "services_status": {
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_percentage": (
                    (healthy_services / total_services * 100)
                    if total_services > 0
                    else 0
                ),
            },
            "performance_metrics": {
                "average_response_time_ms": avg_response_time,
                "meets_response_time_target": avg_response_time
                <= self.target_metrics["response_time_ms"],
                "availability_status": (
                    "high"
                    if health_score >= 90
                    else "moderate" if health_score >= 70 else "low"
                ),
            },
            "constitutional_compliance": {
                "hash_consistency_rate": constitutional_score,
                "meets_compliance_target": constitutional_score >= 75,
            },
            "security_status": {
                "security_scan_completed": "phase1" in phase_results
                and phase_results["phase1"].get("status") != "error",
                "dependency_audit_completed": "phase2" in phase_results
                and phase_results["phase2"].get("status") != "error",
            },
            "testing_coverage": {
                "phases_completed": len(
                    [
                        p
                        for p in phase_results.values()
                        if p.get("status") != "not_found"
                    ]
                ),
                "total_phases": len(phase_results),
                "coverage_percentage": len(
                    [
                        p
                        for p in phase_results.values()
                        if p.get("status") != "not_found"
                    ]
                )
                / len(phase_results)
                * 100,
            },
        }

    def generate_recommendations(
        self, phase_results: Dict[str, Any], health_score: float
    ) -> List[str]:
        """Generate specific recommendations based on test results"""
        logger.info("💡 Generating recommendations...")

        recommendations = []

        # Health score based recommendations
        if health_score < 70:
            recommendations.append(
                "CRITICAL: System health score below 70% - immediate remediation required"
            )
        elif health_score < 85:
            recommendations.append(
                "System health score below 85% - address identified issues before production deployment"
            )

        # Service-specific recommendations
        health_matrix = phase_results.get("phase3_health_matrix", {})
        if health_matrix.get("executive_summary", {}).get("critical_issues", 0) > 0:
            recommendations.append(
                "Fix critical service connectivity issues identified in health matrix"
            )

        # Authentication recommendations
        auth_results = phase_results.get("phase3_authentication", {})
        if auth_results.get("overall_status") == "failed":
            recommendations.append(
                "Resolve authentication service issues - JWT token validation failing"
            )

        # Constitutional compliance recommendations
        constitutional = phase_results.get("phase4", {})
        if (
            constitutional.get("results", {})
            .get("constitutional_hash_consistency", {})
            .get("consistency_rate", 0)
            < 90
        ):
            recommendations.append(
                "Improve constitutional hash consistency across services"
            )

        # Performance recommendations
        performance = phase_results.get("phase5", {})
        if performance.get("summary", {}).get("success_rate", 0) < 100:
            recommendations.append(
                "Address performance issues identified in load testing"
            )

        # Security recommendations
        if phase_results.get("phase1", {}).get("status") == "error":
            recommendations.append("Complete security vulnerability scanning")

        if phase_results.get("phase2", {}).get("status") == "error":
            recommendations.append("Complete dependency security audit")

        # General recommendations
        if not recommendations:
            recommendations.append(
                "System performing well - maintain current monitoring and continue regular health checks"
            )

        recommendations.append(
            "Implement continuous monitoring for all identified metrics"
        )
        recommendations.append("Schedule regular system health assessments")

        return recommendations

    def generate_final_report(self) -> SystemValidationReport:
        """Generate comprehensive final validation report"""
        logger.info("🚀 Generating ACGS-PGP Final System Validation Report...")

        # Load all phase results
        phase_results = self.load_phase_results()

        # Calculate system health score
        health_score = self.calculate_system_health_score(phase_results)

        # Assess operational readiness
        operational_readiness = self.assess_operational_readiness(
            health_score, phase_results
        )

        # Generate executive summary
        executive_summary = self.generate_executive_summary(
            phase_results, health_score, operational_readiness
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(phase_results, health_score)

        # Determine overall status
        if health_score >= 85 and operational_readiness in [
            "production_ready",
            "staging_ready",
        ]:
            overall_status = "PASSED"
        elif health_score >= 70:
            overall_status = "CONDITIONAL_PASS"
        else:
            overall_status = "FAILED"

        # Create final report
        report = SystemValidationReport(
            report_title="ACGS-PGP System Validation Report",
            timestamp=datetime.now(timezone.utc),
            constitutional_hash=self.constitutional_hash,
            overall_status=overall_status,
            system_health_score=health_score,
            operational_readiness=operational_readiness,
            phase_results=phase_results,
            executive_summary=executive_summary,
            recommendations=recommendations,
            next_steps=[
                "Review and implement all recommendations",
                "Address any critical or high-priority issues",
                "Schedule follow-up validation testing",
                "Prepare for production deployment if status is PASSED",
                "Establish ongoing monitoring and maintenance procedures",
            ],
        )

        return report


def main():
    """Main execution function"""
    validator = ACGSFinalValidator()

    try:
        # Generate final validation report
        report = validator.generate_final_report()

        # Save report to file
        report_dict = report.dict()
        with open("acgs_pgp_final_validation_report.json", "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

        # Print executive summary
        print("\n" + "=" * 100)
        print("ACGS-PGP FINAL SYSTEM VALIDATION REPORT")
        print("=" * 100)
        print(f"Report Generated: {report.timestamp}")
        print(f"Constitutional Hash: {report.constitutional_hash}")
        print(f"Overall Status: {report.overall_status}")
        print(f"System Health Score: {report.system_health_score:.1f}%")
        print(f"Operational Readiness: {report.operational_readiness.upper()}")
        print("=" * 100)

        print("\nEXECUTIVE SUMMARY:")
        exec_summary = report.executive_summary
        print(
            f"• Services Status: {exec_summary['services_status']['healthy_services']}/{exec_summary['services_status']['total_services']} healthy ({exec_summary['services_status']['health_percentage']:.1f}%)"
        )
        print(
            f"• Average Response Time: {exec_summary['performance_metrics']['average_response_time_ms']:.1f}ms"
        )
        print(
            f"• Constitutional Compliance: {exec_summary['constitutional_compliance']['hash_consistency_rate']:.1f}%"
        )
        print(
            f"• Testing Coverage: {exec_summary['testing_coverage']['phases_completed']}/{exec_summary['testing_coverage']['total_phases']} phases ({exec_summary['testing_coverage']['coverage_percentage']:.1f}%)"
        )

        print("\nKEY RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"{i}. {rec}")

        print("\nNEXT STEPS:")
        for i, step in enumerate(report.next_steps, 1):
            print(f"{i}. {step}")

        print("=" * 100)

        if report.overall_status == "PASSED":
            print("✅ ACGS-PGP system validation PASSED - Ready for deployment!")
            return 0
        elif report.overall_status == "CONDITIONAL_PASS":
            print(
                "⚠️ ACGS-PGP system validation CONDITIONAL PASS - Address recommendations before production"
            )
            return 0
        else:
            print(
                "❌ ACGS-PGP system validation FAILED - Critical issues must be resolved"
            )
            return 1

    except Exception as e:
        logger.error(f"Final validation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
