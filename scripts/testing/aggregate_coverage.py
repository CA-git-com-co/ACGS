#!/usr/bin/env python3
"""
ACGS Coverage Aggregation Script
Aggregates test coverage reports from all services with constitutional compliance validation.
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class CoverageAggregator:
    """Aggregates test coverage reports from multiple services."""

    def __init__(self, constitutional_hash: str = CONSTITUTIONAL_HASH):
        self.constitutional_hash = constitutional_hash
        self.services = [
            "auth-service",
            "ac-service",
            "integrity-service",
            "fv-service",
            "gs-service",
            "pgc-service",
            "ec-service",
        ]

    def aggregate_coverage_reports(self, artifacts_dir: str = ".") -> dict[str, Any]:
        """Aggregate coverage reports from all services."""
        logger.info("Aggregating coverage reports...")

        aggregated_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "services": {},
            "overall": {
                "total_services": 0,
                "services_above_threshold": 0,
                "average_coverage": 0.0,
                "total_tests": 0,
                "total_passed": 0,
                "overall_success_rate": 0.0,
            },
        }

        total_coverage = 0.0
        total_services = 0
        services_above_threshold = 0
        total_tests = 0
        total_passed = 0

        for service_name in self.services:
            try:
                service_data = self.process_service_coverage(
                    service_name, artifacts_dir
                )

                if service_data:
                    aggregated_data["services"][service_name] = service_data

                    # Update totals
                    total_coverage += service_data["line_coverage"]
                    total_services += 1
                    total_tests += service_data["total_tests"]
                    total_passed += service_data["passed_tests"]

                    # Check threshold compliance
                    threshold = self.get_service_threshold(service_name)
                    if service_data["line_coverage"] >= threshold:
                        services_above_threshold += 1

                    logger.info(
                        f"Processed {service_name}: {service_data['line_coverage']:.1f}% coverage"
                    )
                else:
                    logger.warning(f"No coverage data found for {service_name}")

            except Exception as e:
                logger.error(f"Error processing coverage for {service_name}: {e}")

        # Calculate overall metrics
        if total_services > 0:
            aggregated_data["overall"]["total_services"] = total_services
            aggregated_data["overall"][
                "services_above_threshold"
            ] = services_above_threshold
            aggregated_data["overall"]["average_coverage"] = (
                total_coverage / total_services
            )
            aggregated_data["overall"]["total_tests"] = total_tests
            aggregated_data["overall"]["total_passed"] = total_passed
            aggregated_data["overall"]["overall_success_rate"] = total_passed / max(
                1, total_tests
            )

        logger.info(f"Aggregated coverage from {total_services} services")
        logger.info(
            f"Average coverage: {aggregated_data['overall']['average_coverage']:.1f}%"
        )
        logger.info(
            f"Services above threshold: {services_above_threshold}/{total_services}"
        )

        return aggregated_data

    def process_service_coverage(
        self, service_name: str, artifacts_dir: str
    ) -> dict[str, Any]:
        """Process coverage data for a single service."""
        try:
            # Look for coverage artifacts
            service_artifact_dir = Path(artifacts_dir) / f"{service_name}-coverage"

            if not service_artifact_dir.exists():
                logger.warning(f"Artifact directory not found: {service_artifact_dir}")
                return None

            # Read coverage.json
            coverage_file = service_artifact_dir / "coverage.json"
            test_report_file = service_artifact_dir / "test_report.json"

            coverage_data = {}
            test_data = {}

            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

            if test_report_file.exists():
                with open(test_report_file) as f:
                    test_data = json.load(f)

            # Extract coverage metrics
            service_data = self.extract_coverage_metrics(
                coverage_data, test_data, service_name
            )

            # Validate constitutional compliance
            if not self.validate_constitutional_compliance(service_data, service_name):
                logger.warning(
                    f"Constitutional compliance validation failed for {service_name}"
                )

            return service_data

        except Exception as e:
            logger.error(f"Error processing service coverage for {service_name}: {e}")
            return None

    def extract_coverage_metrics(
        self, coverage_data: dict, test_data: dict, service_name: str
    ) -> dict[str, Any]:
        """Extract coverage metrics from raw data."""
        try:
            # Default values
            service_data = {
                "service_name": service_name,
                "line_coverage": 0.0,
                "branch_coverage": 0.0,
                "function_coverage": 0.0,
                "statement_coverage": 0.0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "constitutional_tests": 0,
                "constitutional_coverage": 0.0,
                "quality_score": 0.0,
                "threshold_compliance": False,
            }

            # Extract from coverage data
            if coverage_data:
                totals = coverage_data.get("totals", {})
                service_data["line_coverage"] = totals.get("percent_covered", 0.0)
                service_data["branch_coverage"] = totals.get(
                    "percent_covered_display", 0.0
                )
                service_data["statement_coverage"] = service_data[
                    "line_coverage"
                ]  # Approximate

                # Extract file-level coverage
                files = coverage_data.get("files", {})
                if files:
                    function_coverages = []
                    for file_path, file_data in files.items():
                        summary = file_data.get("summary", {})
                        if "percent_covered" in summary:
                            function_coverages.append(summary["percent_covered"])

                    if function_coverages:
                        service_data["function_coverage"] = sum(
                            function_coverages
                        ) / len(function_coverages)

            # Extract from test data
            if test_data:
                summary = test_data.get("summary", {})
                service_data["total_tests"] = summary.get("total", 0)
                service_data["passed_tests"] = summary.get("passed", 0)
                service_data["failed_tests"] = summary.get("failed", 0)
                service_data["skipped_tests"] = summary.get("skipped", 0)

                # Count constitutional compliance tests
                tests = test_data.get("tests", [])
                constitutional_tests = [
                    test
                    for test in tests
                    if "constitutional" in test.get("nodeid", "").lower()
                    or "constitutional" in test.get("keywords", [])
                ]
                service_data["constitutional_tests"] = len(constitutional_tests)

                # Calculate constitutional coverage
                if constitutional_tests:
                    passed_constitutional = len(
                        [
                            test
                            for test in constitutional_tests
                            if test.get("outcome") == "passed"
                        ]
                    )
                    service_data["constitutional_coverage"] = (
                        passed_constitutional / len(constitutional_tests)
                    ) * 100.0
                else:
                    service_data["constitutional_coverage"] = 0.0

            # Calculate quality score
            service_data["quality_score"] = self.calculate_quality_score(service_data)

            # Check threshold compliance
            threshold = self.get_service_threshold(service_name)
            service_data["threshold_compliance"] = (
                service_data["line_coverage"] >= threshold
            )

            return service_data

        except Exception as e:
            logger.error(f"Error extracting coverage metrics: {e}")
            return service_data

    def calculate_quality_score(self, service_data: dict[str, Any]) -> float:
        """Calculate overall quality score for a service."""
        try:
            # Weighted scoring
            weights = {
                "line_coverage": 0.3,
                "branch_coverage": 0.25,
                "function_coverage": 0.2,
                "test_success_rate": 0.15,
                "constitutional_compliance": 0.1,
            }

            # Calculate individual scores
            line_score = min(100.0, service_data["line_coverage"]) / 100.0
            branch_score = min(100.0, service_data["branch_coverage"]) / 100.0
            function_score = min(100.0, service_data["function_coverage"]) / 100.0

            success_rate = service_data["passed_tests"] / max(
                1, service_data["total_tests"]
            )
            constitutional_score = (
                min(100.0, service_data["constitutional_coverage"]) / 100.0
            )

            # Calculate weighted score
            quality_score = (
                line_score * weights["line_coverage"]
                + branch_score * weights["branch_coverage"]
                + function_score * weights["function_coverage"]
                + success_rate * weights["test_success_rate"]
                + constitutional_score * weights["constitutional_compliance"]
            ) * 100.0

            return quality_score

        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.0

    def get_service_threshold(self, service_name: str) -> float:
        """Get coverage threshold for a service."""
        # Critical services have higher thresholds
        critical_services = ["ac-service", "pgc-service", "ec-service"]

        if service_name in critical_services:
            return 95.0
        if service_name == "auth-service":
            return 92.0
        return 90.0

    def validate_constitutional_compliance(
        self, service_data: dict[str, Any], service_name: str
    ) -> bool:
        """Validate constitutional compliance for service coverage."""
        try:
            # Check if service requires constitutional compliance
            critical_services = ["ac-service", "pgc-service", "ec-service"]

            if service_name in critical_services:
                # Require constitutional tests
                if service_data["constitutional_tests"] < 5:
                    logger.warning(
                        f"Insufficient constitutional tests for {service_name}: {service_data['constitutional_tests']}"
                    )
                    return False

                # Require high constitutional coverage
                if service_data["constitutional_coverage"] < 95.0:
                    logger.warning(
                        f"Low constitutional coverage for {service_name}: {service_data['constitutional_coverage']:.1f}%"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating constitutional compliance: {e}")
            return False

    def save_aggregated_report(self, aggregated_data: dict[str, Any], output_file: str):
        """Save aggregated coverage report to file."""
        try:
            with open(output_file, "w") as f:
                json.dump(aggregated_data, f, indent=2, default=str)

            logger.info(f"Aggregated coverage report saved to: {output_file}")

        except Exception as e:
            logger.error(f"Error saving aggregated report: {e}")
            raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Aggregate ACGS test coverage reports")
    parser.add_argument(
        "--constitutional-hash",
        default=CONSTITUTIONAL_HASH,
        help="Constitutional hash for validation",
    )
    parser.add_argument(
        "--artifacts-dir", default=".", help="Directory containing coverage artifacts"
    )
    parser.add_argument(
        "--output-file",
        default="aggregated_coverage.json",
        help="Output file for aggregated coverage",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create aggregator
        aggregator = CoverageAggregator(args.constitutional_hash)

        # Aggregate coverage reports
        aggregated_data = aggregator.aggregate_coverage_reports(args.artifacts_dir)

        # Save report
        aggregator.save_aggregated_report(aggregated_data, args.output_file)

        # Print summary
        overall = aggregated_data["overall"]
        print(f"\n{'=' * 60}")
        print("ACGS COVERAGE AGGREGATION SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total Services: {overall['total_services']}")
        print(f"Average Coverage: {overall['average_coverage']:.1f}%")
        print(
            f"Services Above Threshold: {overall['services_above_threshold']}/{overall['total_services']}"
        )
        print(f"Total Tests: {overall['total_tests']}")
        print(f"Overall Success Rate: {overall['overall_success_rate']:.1%}")
        print(f"Constitutional Hash: {aggregated_data['constitutional_hash']}")
        print(f"{'=' * 60}")

        # Exit with appropriate code
        if overall["services_above_threshold"] == overall["total_services"]:
            print("✅ All services meet coverage thresholds")
            exit(0)
        else:
            print("❌ Some services below coverage thresholds")
            exit(1)

    except Exception as e:
        logger.error(f"Coverage aggregation failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
