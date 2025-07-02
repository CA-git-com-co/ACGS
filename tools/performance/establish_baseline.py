#!/usr/bin/env python3
"""
ACGS Performance Baseline Establishment Script
Establishes comprehensive performance baselines for all ACGS services.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the infrastructure monitoring path to sys.path
sys.path.append(
    str(Path(__file__).parent.parent.parent / "infrastructure/monitoring/performance")
)

from baseline_metrics_collector import PerformanceBaselineCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class BaselineEstablisher:
    """Establishes and manages ACGS performance baselines."""

    def __init__(self):
        self.collector = PerformanceBaselineCollector()

    async def establish_comprehensive_baseline(self, duration_hours: int = 24):
        """Establish comprehensive performance baseline."""
        logger.info(
            f"Starting comprehensive baseline establishment for {duration_hours} hours..."
        )

        try:
            # Pre-flight checks
            await self.perform_preflight_checks()

            # Establish baseline
            baseline = await self.collector.establish_performance_baseline(
                duration_hours
            )

            # Generate reports
            await self.generate_baseline_reports(baseline)

            # Validate baseline
            await self.validate_baseline(baseline)

            logger.info("Comprehensive baseline establishment completed successfully!")
            return baseline

        except Exception as e:
            logger.error(f"Baseline establishment failed: {e}")
            raise

    async def perform_preflight_checks(self):
        """Perform pre-flight checks before baseline establishment."""
        logger.info("Performing pre-flight checks...")

        # Check service availability
        services_status = {}
        for service_name, port in self.collector.services.items():
            try:
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:{port}/health", timeout=10
                    ) as response:
                        services_status[service_name] = {
                            "available": response.status == 200,
                            "status_code": response.status,
                        }
            except Exception as e:
                services_status[service_name] = {"available": False, "error": str(e)}

        # Check if enough services are available
        available_services = sum(
            1 for status in services_status.values() if status["available"]
        )
        total_services = len(services_status)

        if (
            available_services < total_services * 0.8
        ):  # At least 80% services should be available
            raise RuntimeError(
                f"Only {available_services}/{total_services} services available. Need at least 80% for baseline."
            )

        logger.info(
            f"✓ Pre-flight checks passed: {available_services}/{total_services} services available"
        )

        # Log service status
        for service_name, status in services_status.items():
            if status["available"]:
                logger.info(f"  ✓ {service_name}: Available")
            else:
                logger.warning(
                    f"  ✗ {service_name}: Unavailable - {status.get('error', 'Unknown error')}"
                )

    async def generate_baseline_reports(self, baseline):
        """Generate comprehensive baseline reports."""
        logger.info("Generating baseline reports...")

        # Create reports directory
        reports_dir = Path("reports/performance_baselines")
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Generate summary report
        summary_report = self.generate_summary_report(baseline)
        summary_file = reports_dir / f"baseline_summary_{baseline.baseline_id}.json"
        with open(summary_file, "w") as f:
            json.dump(summary_report, f, indent=2)

        # Generate detailed report
        detailed_report = self.generate_detailed_report(baseline)
        detailed_file = reports_dir / f"baseline_detailed_{baseline.baseline_id}.json"
        with open(detailed_file, "w") as f:
            json.dump(detailed_report, f, indent=2)

        # Generate markdown report
        markdown_report = self.generate_markdown_report(baseline)
        markdown_file = reports_dir / f"baseline_report_{baseline.baseline_id}.md"
        with open(markdown_file, "w") as f:
            f.write(markdown_report)

        logger.info(f"Reports generated in {reports_dir}")

    def generate_summary_report(self, baseline) -> dict:
        """Generate summary report."""
        return {
            "baseline_summary": {
                "baseline_id": baseline.baseline_id,
                "version": baseline.version,
                "created_at": baseline.created_at.isoformat(),
                "measurement_duration_hours": baseline.measurement_duration_hours,
                "sample_count": baseline.sample_count,
                "constitutional_hash": baseline.constitutional_hash,
            },
            "system_performance": {
                "overall_avg_response_time_ms": baseline.overall_avg_response_time,
                "overall_error_rate_percent": baseline.overall_error_rate,
                "overall_throughput_rps": baseline.overall_throughput,
                "overall_constitutional_compliance_percent": baseline.overall_constitutional_compliance
                * 100,
            },
            "service_count": len(baseline.services),
            "services_summary": {
                service_name: {
                    "avg_response_time_ms": metrics.avg_response_time,
                    "p95_response_time_ms": metrics.p95_response_time,
                    "error_rate_percent": metrics.error_rate_percent,
                    "uptime_percent": metrics.uptime_percent,
                    "constitutional_compliance_percent": metrics.constitutional_compliance_rate
                    * 100,
                }
                for service_name, metrics in baseline.services.items()
            },
            "performance_targets": {
                "target_response_time_ms": 500,  # <500ms SLA
                "target_error_rate_percent": 1.0,  # <1% SLA
                "target_uptime_percent": 99.9,  # >99.9% SLA
                "target_constitutional_compliance_percent": 95.0,  # >95% SLA
            },
            "sla_compliance": self.check_sla_compliance(baseline),
        }

    def generate_detailed_report(self, baseline) -> dict:
        """Generate detailed report."""
        return {
            "baseline_metadata": {
                "baseline_id": baseline.baseline_id,
                "version": baseline.version,
                "created_at": baseline.created_at.isoformat(),
                "measurement_duration_hours": baseline.measurement_duration_hours,
                "sample_count": baseline.sample_count,
                "constitutional_hash": baseline.constitutional_hash,
            },
            "detailed_metrics": {
                service_name: {
                    "service_name": metrics.service_name,
                    "port": metrics.port,
                    "response_times": {
                        "avg_ms": metrics.avg_response_time,
                        "p50_ms": metrics.p50_response_time,
                        "p95_ms": metrics.p95_response_time,
                        "p99_ms": metrics.p99_response_time,
                        "max_ms": metrics.max_response_time,
                    },
                    "throughput": {
                        "avg_rps": metrics.avg_throughput,
                        "peak_rps": metrics.peak_throughput,
                    },
                    "reliability": {
                        "error_rate_percent": metrics.error_rate_percent,
                        "uptime_percent": metrics.uptime_percent,
                        "health_check_success_rate": metrics.health_check_success_rate,
                    },
                    "constitutional_compliance": {
                        "compliance_rate": metrics.constitutional_compliance_rate,
                        "validation_time_ms": metrics.constitutional_validation_time_ms,
                    },
                    "resource_utilization": {
                        "avg_cpu_percent": metrics.avg_cpu_percent,
                        "avg_memory_mb": metrics.avg_memory_mb,
                    },
                    "timestamps": {
                        "baseline_established": metrics.baseline_established.isoformat(),
                        "last_updated": metrics.last_updated.isoformat(),
                    },
                }
                for service_name, metrics in baseline.services.items()
            },
            "system_wide_analysis": {
                "performance_distribution": self.analyze_performance_distribution(
                    baseline
                ),
                "bottleneck_analysis": self.analyze_bottlenecks(baseline),
                "constitutional_compliance_analysis": self.analyze_constitutional_compliance(
                    baseline
                ),
            },
        }

    def generate_markdown_report(self, baseline) -> str:
        """Generate markdown report."""
        report = f"""# ACGS Performance Baseline Report

## Baseline Information
- **Baseline ID**: {baseline.baseline_id}
- **Version**: {baseline.version}
- **Created**: {baseline.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
- **Duration**: {baseline.measurement_duration_hours} hours
- **Samples**: {baseline.sample_count}
- **Constitutional Hash**: `{baseline.constitutional_hash}`

## System Performance Overview

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Avg Response Time | {baseline.overall_avg_response_time:.2f}ms | <500ms | {"✅" if baseline.overall_avg_response_time < 500 else "❌"} |
| Error Rate | {baseline.overall_error_rate:.2f}% | <1% | {"✅" if baseline.overall_error_rate < 1 else "❌"} |
| Throughput | {baseline.overall_throughput:.2f} RPS | - | - |
| Constitutional Compliance | {baseline.overall_constitutional_compliance * 100:.1f}% | >95% | {"✅" if baseline.overall_constitutional_compliance > 0.95 else "❌"} |

## Service Performance Details

"""

        for service_name, metrics in baseline.services.items():
            report += f"""### {service_name} (Port {metrics.port})

| Metric | Value |
|--------|-------|
| Avg Response Time | {metrics.avg_response_time:.2f}ms |
| P95 Response Time | {metrics.p95_response_time:.2f}ms |
| P99 Response Time | {metrics.p99_response_time:.2f}ms |
| Error Rate | {metrics.error_rate_percent:.2f}% |
| Uptime | {metrics.uptime_percent:.2f}% |
| Constitutional Compliance | {metrics.constitutional_compliance_rate * 100:.1f}% |
| Avg Throughput | {metrics.avg_throughput:.2f} RPS |

"""

        # Add SLA compliance summary
        sla_compliance = self.check_sla_compliance(baseline)
        report += f"""## SLA Compliance Summary

- **Response Time SLA**: {"✅ PASS" if sla_compliance["response_time_sla"] else "❌ FAIL"}
- **Error Rate SLA**: {"✅ PASS" if sla_compliance["error_rate_sla"] else "❌ FAIL"}
- **Constitutional Compliance SLA**: {"✅ PASS" if sla_compliance["constitutional_compliance_sla"] else "❌ FAIL"}

## Recommendations

"""

        # Add recommendations
        recommendations = self.generate_recommendations(baseline)
        for recommendation in recommendations:
            report += f"- {recommendation}\n"

        return report

    def check_sla_compliance(self, baseline) -> dict:
        """Check SLA compliance."""
        return {
            "response_time_sla": baseline.overall_avg_response_time < 500,  # <500ms
            "error_rate_sla": baseline.overall_error_rate < 1.0,  # <1%
            "constitutional_compliance_sla": baseline.overall_constitutional_compliance
            > 0.95,  # >95%
            "overall_sla_compliance": (
                baseline.overall_avg_response_time < 500
                and baseline.overall_error_rate < 1.0
                and baseline.overall_constitutional_compliance > 0.95
            ),
        }

    def analyze_performance_distribution(self, baseline) -> dict:
        """Analyze performance distribution across services."""
        response_times = [
            metrics.avg_response_time for metrics in baseline.services.values()
        ]
        error_rates = [
            metrics.error_rate_percent for metrics in baseline.services.values()
        ]

        return {
            "response_time_stats": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "avg": (
                    sum(response_times) / len(response_times) if response_times else 0
                ),
            },
            "error_rate_stats": {
                "min": min(error_rates) if error_rates else 0,
                "max": max(error_rates) if error_rates else 0,
                "avg": sum(error_rates) / len(error_rates) if error_rates else 0,
            },
        }

    def analyze_bottlenecks(self, baseline) -> list:
        """Analyze potential bottlenecks."""
        bottlenecks = []

        for service_name, metrics in baseline.services.items():
            if metrics.avg_response_time > 200:  # >200ms is concerning
                bottlenecks.append(
                    {
                        "service": service_name,
                        "type": "high_response_time",
                        "value": metrics.avg_response_time,
                        "severity": (
                            "high" if metrics.avg_response_time > 500 else "medium"
                        ),
                    }
                )

            if metrics.error_rate_percent > 0.5:  # >0.5% error rate
                bottlenecks.append(
                    {
                        "service": service_name,
                        "type": "high_error_rate",
                        "value": metrics.error_rate_percent,
                        "severity": (
                            "high" if metrics.error_rate_percent > 2 else "medium"
                        ),
                    }
                )

        return bottlenecks

    def analyze_constitutional_compliance(self, baseline) -> dict:
        """Analyze constitutional compliance across services."""
        compliance_rates = [
            metrics.constitutional_compliance_rate
            for metrics in baseline.services.values()
        ]

        return {
            "avg_compliance": (
                sum(compliance_rates) / len(compliance_rates)
                if compliance_rates
                else 1.0
            ),
            "min_compliance": min(compliance_rates) if compliance_rates else 1.0,
            "services_below_95_percent": [
                service_name
                for service_name, metrics in baseline.services.items()
                if metrics.constitutional_compliance_rate < 0.95
            ],
        }

    def generate_recommendations(self, baseline) -> list:
        """Generate performance recommendations."""
        recommendations = []

        # Check response times
        if baseline.overall_avg_response_time > 200:
            recommendations.append(
                "Consider optimizing response times - current average exceeds 200ms"
            )

        # Check error rates
        if baseline.overall_error_rate > 0.5:
            recommendations.append(
                "Investigate error sources - error rate exceeds 0.5%"
            )

        # Check constitutional compliance
        if baseline.overall_constitutional_compliance < 0.98:
            recommendations.append(
                "Review constitutional compliance implementation - compliance below 98%"
            )

        # Service-specific recommendations
        for service_name, metrics in baseline.services.items():
            if metrics.avg_response_time > 300:
                recommendations.append(
                    f"Optimize {service_name} performance - response time {metrics.avg_response_time:.1f}ms"
                )

            if metrics.error_rate_percent > 1:
                recommendations.append(
                    f"Address {service_name} errors - error rate {metrics.error_rate_percent:.1f}%"
                )

        if not recommendations:
            recommendations.append(
                "All services performing within acceptable parameters"
            )

        return recommendations

    async def validate_baseline(self, baseline):
        """Validate the established baseline."""
        logger.info("Validating baseline...")

        # Check if baseline has sufficient data
        if baseline.sample_count < 10:
            logger.warning(f"Low sample count: {baseline.sample_count}")

        # Check if all services have data
        missing_services = []
        for service_name in self.collector.services.keys():
            if service_name not in baseline.services:
                missing_services.append(service_name)

        if missing_services:
            logger.warning(f"Missing baseline data for services: {missing_services}")

        # Check SLA compliance
        sla_compliance = self.check_sla_compliance(baseline)
        if not sla_compliance["overall_sla_compliance"]:
            logger.warning("Baseline indicates SLA non-compliance")

        logger.info("✓ Baseline validation completed")


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Establish ACGS performance baseline")
    parser.add_argument(
        "--duration",
        type=int,
        default=1,
        help="Baseline duration in hours (default: 1)",
    )
    parser.add_argument(
        "--quick", action="store_true", help="Quick baseline (15 minutes)"
    )

    args = parser.parse_args()

    duration_hours = 0.25 if args.quick else args.duration  # 15 minutes for quick

    establisher = BaselineEstablisher()

    try:
        baseline = await establisher.establish_comprehensive_baseline(duration_hours)

        print("\n" + "=" * 60)
        print("ACGS PERFORMANCE BASELINE ESTABLISHED")
        print("=" * 60)
        print(f"Baseline ID: {baseline.baseline_id}")
        print(f"Duration: {baseline.measurement_duration_hours} hours")
        print(f"Samples: {baseline.sample_count}")
        print(f"Services: {len(baseline.services)}")
        print(f"Avg Response Time: {baseline.overall_avg_response_time:.2f}ms")
        print(f"Error Rate: {baseline.overall_error_rate:.2f}%")
        print(
            f"Constitutional Compliance: {baseline.overall_constitutional_compliance * 100:.1f}%"
        )
        print("=" * 60)

    except Exception as e:
        logger.error(f"Failed to establish baseline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
