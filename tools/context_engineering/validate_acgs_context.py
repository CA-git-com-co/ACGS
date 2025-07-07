#!/usr/bin/env python3
"""
ACGS Context Engineering Validation Framework

This tool validates that ACGS Context Engineering principles are properly
implemented across the codebase with constitutional compliance and performance targets.

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import redis.asyncio as redis
from pydantic import BaseModel, Field

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS Context Engineering validation targets
VALIDATION_TARGETS = {
    "constitutional_compliance_rate": 1.0,  # 100% compliance required
    "performance_p99_latency_ms": 5.0,
    "performance_throughput_rps": 100,
    "cache_hit_rate": 0.85,
    "context_engineering_coverage": 0.90,  # 90% of services should use Context Engineering patterns
    "prp_template_compliance": 1.0,  # 100% PRP compliance
}


class ContextEngineeringValidationResult(BaseModel):
    """Result of Context Engineering validation."""

    component: str
    validation_type: str
    passed: bool
    score: float
    target: float
    details: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ACGSContextEngineeringValidator:
    """
    Comprehensive validator for ACGS Context Engineering implementation.

    Validates:
    - Constitutional compliance in all Context Engineering components
    - Performance targets for Context Engineering operations
    - Multi-agent coordination Context Engineering patterns
    - PRP template compliance and coverage
    - Testing framework Context Engineering integration
    """

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.validation_results: List[ContextEngineeringValidationResult] = []

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("acgs.context_engineering.validator")

        # Validation targets
        self.targets = VALIDATION_TARGETS

        # ACGS service endpoints for validation
        self.services = {
            "constitutional-ai": "http://localhost:8001",
            "integrity": "http://localhost:8002",
            "multi-agent-coordinator": "http://localhost:8008",
            "worker-agents": "http://localhost:8009",
            "blackboard": "http://localhost:8010",
            "authentication": "http://localhost:8016",
        }

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive Context Engineering validation."""
        self.logger.info("🚀 Starting ACGS Context Engineering Validation")
        self.logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        self.logger.info(f"Validation Targets: {self.targets}")

        start_time = time.time()

        # Reset validation results
        self.validation_results = []

        # Run validation categories
        await self._validate_constitutional_compliance()
        await self._validate_prp_template_compliance()
        await self._validate_context_engineering_patterns()
        await self._validate_testing_framework_integration()
        await self._validate_performance_targets()
        await self._validate_multi_agent_coordination()

        # Generate comprehensive report
        total_time = time.time() - start_time
        validation_summary = self._generate_validation_summary(total_time)

        self.logger.info(
            f"✅ Context Engineering validation completed in {total_time:.2f}s"
        )

        return validation_summary

    async def _validate_constitutional_compliance(self):
        """Validate constitutional compliance in Context Engineering components."""
        self.logger.info(
            "📋 Validating Constitutional Compliance in Context Engineering"
        )

        # Check CLAUDE_CONTEXT_ENGINEERING.md
        claude_ce_file = self.base_path / "CLAUDE_CONTEXT_ENGINEERING.md"
        if claude_ce_file.exists():
            content = claude_ce_file.read_text()
            hash_count = content.count(CONSTITUTIONAL_HASH)
            constitutional_compliance = (
                hash_count >= 10
            )  # Should have multiple references

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="CLAUDE_CONTEXT_ENGINEERING.md",
                    validation_type="constitutional_compliance",
                    passed=constitutional_compliance,
                    score=1.0 if constitutional_compliance else 0.0,
                    target=1.0,
                    details={
                        "constitutional_hash_references": hash_count,
                        "file_exists": True,
                    },
                )
            )
        else:
            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="CLAUDE_CONTEXT_ENGINEERING.md",
                    validation_type="constitutional_compliance",
                    passed=False,
                    score=0.0,
                    target=1.0,
                    details={"file_exists": False},
                )
            )

        # Check PRP templates for constitutional compliance
        prp_template_file = self.base_path / "PRPs" / "templates" / "acgs_prp_base.md"
        if prp_template_file.exists():
            content = prp_template_file.read_text()
            has_constitutional_hash = CONSTITUTIONAL_HASH in content
            has_constitutional_requirements = (
                "Constitutional Compliance Requirement" in content
            )

            constitutional_compliance = (
                has_constitutional_hash and has_constitutional_requirements
            )

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="PRP_Template",
                    validation_type="constitutional_compliance",
                    passed=constitutional_compliance,
                    score=1.0 if constitutional_compliance else 0.0,
                    target=1.0,
                    details={
                        "has_constitutional_hash": has_constitutional_hash,
                        "has_constitutional_requirements": has_constitutional_requirements,
                    },
                )
            )

        # Check Context Engineering examples for constitutional compliance
        examples_dir = self.base_path / "services" / "examples" / "context_engineering"
        if examples_dir.exists():
            example_files = list(examples_dir.rglob("*.py"))
            compliant_files = 0

            for file_path in example_files:
                content = file_path.read_text()
                if CONSTITUTIONAL_HASH in content:
                    compliant_files += 1

            compliance_rate = (
                compliant_files / len(example_files) if example_files else 0
            )

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Context_Engineering_Examples",
                    validation_type="constitutional_compliance",
                    passed=compliance_rate >= 0.9,
                    score=compliance_rate,
                    target=0.9,
                    details={
                        "total_files": len(example_files),
                        "compliant_files": compliant_files,
                        "compliance_rate": compliance_rate,
                    },
                )
            )

    async def _validate_prp_template_compliance(self):
        """Validate PRP template structure and compliance."""
        self.logger.info("📋 Validating PRP Template Compliance")

        # Check PRP template structure
        prp_template_file = self.base_path / "PRPs" / "templates" / "acgs_prp_base.md"
        if prp_template_file.exists():
            content = prp_template_file.read_text()

            required_sections = [
                "## Goal",
                "## Why",
                "## What",
                "## Context",
                "## Blueprint",
                "## Validation",
                "## Checklist",
            ]

            sections_present = sum(
                1 for section in required_sections if section in content
            )
            compliance_score = sections_present / len(required_sections)

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="PRP_Template_Structure",
                    validation_type="template_compliance",
                    passed=compliance_score >= 1.0,
                    score=compliance_score,
                    target=1.0,
                    details={
                        "required_sections": len(required_sections),
                        "sections_present": sections_present,
                        "missing_sections": [
                            s for s in required_sections if s not in content
                        ],
                    },
                )
            )

            # Check ACGS-specific template content
            acgs_requirements = [
                "Constitutional Hash",
                "Performance Requirements",
                "Multi-Agent Integration",
                "Blackboard Service",
                "Constitutional AI Service",
                "ACGS Integration Points",
            ]

            acgs_content_present = sum(1 for req in acgs_requirements if req in content)
            acgs_compliance = acgs_content_present / len(acgs_requirements)

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="PRP_Template_ACGS_Content",
                    validation_type="acgs_compliance",
                    passed=acgs_compliance >= 0.9,
                    score=acgs_compliance,
                    target=0.9,
                    details={
                        "acgs_requirements": len(acgs_requirements),
                        "content_present": acgs_content_present,
                        "missing_content": [
                            req for req in acgs_requirements if req not in content
                        ],
                    },
                )
            )

        # Check PRP examples
        prp_examples_dir = self.base_path / "PRPs" / "examples"
        if prp_examples_dir.exists():
            example_files = list(prp_examples_dir.glob("*.md"))
            valid_examples = 0

            for file_path in example_files:
                content = file_path.read_text()
                has_constitutional_hash = CONSTITUTIONAL_HASH in content
                has_performance_targets = "Performance Requirements" in content
                has_validation_section = "## Validation" in content

                if (
                    has_constitutional_hash
                    and has_performance_targets
                    and has_validation_section
                ):
                    valid_examples += 1

            example_compliance = (
                valid_examples / len(example_files) if example_files else 0
            )

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="PRP_Examples",
                    validation_type="example_compliance",
                    passed=example_compliance >= 0.8,
                    score=example_compliance,
                    target=0.8,
                    details={
                        "total_examples": len(example_files),
                        "valid_examples": valid_examples,
                        "compliance_rate": example_compliance,
                    },
                )
            )

    async def _validate_context_engineering_patterns(self):
        """Validate Context Engineering pattern implementation."""
        self.logger.info("📋 Validating Context Engineering Patterns")

        # Check constitutional service pattern
        constitutional_pattern_file = (
            self.base_path
            / "services"
            / "examples"
            / "context_engineering"
            / "patterns"
            / "constitutional_service_pattern.py"
        )

        if constitutional_pattern_file.exists():
            content = constitutional_pattern_file.read_text()

            pattern_requirements = [
                "CONSTITUTIONAL_HASH",
                "ConstitutionalServiceExample",
                "validate_constitutional_compliance",
                "track_latency",
                "AsyncMock",
                "FastAPI",
            ]

            requirements_met = sum(1 for req in pattern_requirements if req in content)
            pattern_compliance = requirements_met / len(pattern_requirements)

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Constitutional_Service_Pattern",
                    validation_type="pattern_compliance",
                    passed=pattern_compliance >= 0.9,
                    score=pattern_compliance,
                    target=0.9,
                    details={
                        "pattern_requirements": len(pattern_requirements),
                        "requirements_met": requirements_met,
                        "missing_requirements": [
                            req for req in pattern_requirements if req not in content
                        ],
                    },
                )
            )

        # Check multi-agent coordination pattern
        coordination_pattern_file = (
            self.base_path
            / "services"
            / "examples"
            / "context_engineering"
            / "multi_agent"
            / "blackboard_coordination.py"
        )

        if coordination_pattern_file.exists():
            content = coordination_pattern_file.read_text()

            coordination_requirements = [
                "BlackboardCoordinator",
                "CoordinationMessage",
                "CONSTITUTIONAL_HASH",
                "AgentType",
                "redis.asyncio",
            ]

            requirements_met = sum(
                1 for req in coordination_requirements if req in content
            )
            coordination_compliance = requirements_met / len(coordination_requirements)

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Multi_Agent_Coordination_Pattern",
                    validation_type="pattern_compliance",
                    passed=coordination_compliance >= 0.9,
                    score=coordination_compliance,
                    target=0.9,
                    details={
                        "coordination_requirements": len(coordination_requirements),
                        "requirements_met": requirements_met,
                    },
                )
            )

        # Check testing framework pattern
        testing_pattern_file = (
            self.base_path
            / "services"
            / "examples"
            / "context_engineering"
            / "testing"
            / "constitutional_test_case.py"
        )

        if testing_pattern_file.exists():
            content = testing_pattern_file.read_text()

            testing_requirements = [
                "ConstitutionalTestCase",
                "validate_constitutional_hash",
                "validate_latency_target",
                "validate_blackboard_integration",
                "pytest",
            ]

            requirements_met = sum(1 for req in testing_requirements if req in content)
            testing_compliance = requirements_met / len(testing_requirements)

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Constitutional_Testing_Pattern",
                    validation_type="pattern_compliance",
                    passed=testing_compliance >= 0.9,
                    score=testing_compliance,
                    target=0.9,
                    details={
                        "testing_requirements": len(testing_requirements),
                        "requirements_met": requirements_met,
                    },
                )
            )

    async def _validate_testing_framework_integration(self):
        """Validate Context Engineering integration with ACGS testing framework."""
        self.logger.info("📋 Validating Testing Framework Integration")

        # Check if existing ACGS tests use Context Engineering patterns
        test_runner_file = self.base_path / "tests" / "run_acgs_comprehensive_tests.py"
        if test_runner_file.exists():
            content = test_runner_file.read_text()

            has_constitutional_compliance = "constitutional-compliance" in content
            has_context_engineering = (
                "context_engineering" in content or "constitutional" in content
            )
            has_performance_validation = "performance" in content

            integration_score = (
                sum(
                    [
                        has_constitutional_compliance,
                        has_context_engineering,
                        has_performance_validation,
                    ]
                )
                / 3
            )

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="ACGS_Test_Runner_Integration",
                    validation_type="testing_integration",
                    passed=integration_score >= 0.7,
                    score=integration_score,
                    target=0.7,
                    details={
                        "has_constitutional_compliance": has_constitutional_compliance,
                        "has_context_engineering": has_context_engineering,
                        "has_performance_validation": has_performance_validation,
                    },
                )
            )

        # Check for Context Engineering test examples
        ce_test_files = list((self.base_path / "tests").rglob("*context_engineering*"))
        ce_test_files.extend(list((self.base_path / "tests").rglob("*constitutional*")))

        self.validation_results.append(
            ContextEngineeringValidationResult(
                component="Context_Engineering_Test_Files",
                validation_type="test_coverage",
                passed=len(ce_test_files) >= 3,
                score=min(len(ce_test_files) / 3, 1.0),
                target=1.0,
                details={
                    "context_engineering_test_files": len(ce_test_files),
                    "test_files": [
                        str(f.relative_to(self.base_path)) for f in ce_test_files[:5]
                    ],
                },
            )
        )

    async def _validate_performance_targets(self):
        """Validate Context Engineering performance targets."""
        self.logger.info("📋 Validating Performance Targets")

        # Check if services are available for performance testing
        available_services = []
        performance_results = {}

        async with aiohttp.ClientSession() as session:
            for service_name, service_url in self.services.items():
                try:
                    start_time = time.perf_counter()
                    async with session.get(
                        f"{service_url}/health", timeout=2
                    ) as response:
                        latency_ms = (time.perf_counter() - start_time) * 1000

                        if response.status == 200:
                            available_services.append(service_name)
                            performance_results[service_name] = {
                                "latency_ms": latency_ms,
                                "available": True,
                            }

                except Exception as e:
                    performance_results[service_name] = {
                        "available": False,
                        "error": str(e),
                    }

        # Calculate performance compliance
        available_count = len(available_services)
        total_services = len(self.services)
        availability_score = available_count / total_services

        # Check latency targets for available services
        latency_compliant_services = 0
        for service_name in available_services:
            if (
                performance_results[service_name]["latency_ms"]
                <= self.targets["performance_p99_latency_ms"]
            ):
                latency_compliant_services += 1

        latency_compliance = (
            latency_compliant_services / available_count if available_count > 0 else 0
        )

        self.validation_results.append(
            ContextEngineeringValidationResult(
                component="Service_Availability",
                validation_type="performance_availability",
                passed=availability_score >= 0.7,
                score=availability_score,
                target=0.7,
                details={
                    "available_services": available_count,
                    "total_services": total_services,
                    "available_service_names": available_services,
                    "performance_results": performance_results,
                },
            )
        )

        self.validation_results.append(
            ContextEngineeringValidationResult(
                component="Latency_Compliance",
                validation_type="performance_latency",
                passed=latency_compliance >= 0.8,
                score=latency_compliance,
                target=0.8,
                details={
                    "latency_compliant_services": latency_compliant_services,
                    "available_services": available_count,
                    "latency_target_ms": self.targets["performance_p99_latency_ms"],
                },
            )
        )

    async def _validate_multi_agent_coordination(self):
        """Validate multi-agent coordination Context Engineering patterns."""
        self.logger.info("📋 Validating Multi-Agent Coordination")

        # Check blackboard service integration
        try:
            redis_client = redis.from_url("redis://localhost:6389/1")
            await redis_client.ping()

            # Test constitutional compliance in blackboard
            test_key = f"test:context_engineering:{int(time.time())}"
            test_data = {
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "context_engineering_test": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await redis_client.setex(test_key, 10, json.dumps(test_data))
            stored_data = await redis_client.get(test_key)

            blackboard_functional = stored_data is not None
            if stored_data:
                parsed_data = json.loads(stored_data)
                constitutional_compliant = (
                    parsed_data.get("constitutional_hash") == CONSTITUTIONAL_HASH
                )
            else:
                constitutional_compliant = False

            # Cleanup
            await redis_client.delete(test_key)
            await redis_client.close()

            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Blackboard_Service",
                    validation_type="multi_agent_coordination",
                    passed=blackboard_functional and constitutional_compliant,
                    score=(
                        1.0
                        if (blackboard_functional and constitutional_compliant)
                        else 0.0
                    ),
                    target=1.0,
                    details={
                        "blackboard_functional": blackboard_functional,
                        "constitutional_compliant": constitutional_compliant,
                    },
                )
            )

        except Exception as e:
            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Blackboard_Service",
                    validation_type="multi_agent_coordination",
                    passed=False,
                    score=0.0,
                    target=1.0,
                    details={"error": str(e)},
                )
            )

        # Check multi-agent coordinator integration
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:8008/health", timeout=2
                ) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        constitutional_compliant = (
                            health_data.get("constitutional_hash")
                            == CONSTITUTIONAL_HASH
                        )

                        self.validation_results.append(
                            ContextEngineeringValidationResult(
                                component="Multi_Agent_Coordinator",
                                validation_type="multi_agent_coordination",
                                passed=constitutional_compliant,
                                score=1.0 if constitutional_compliant else 0.0,
                                target=1.0,
                                details={
                                    "service_available": True,
                                    "constitutional_compliant": constitutional_compliant,
                                    "health_data": health_data,
                                },
                            )
                        )
                    else:
                        raise Exception(f"Health check failed: {response.status}")

        except Exception as e:
            self.validation_results.append(
                ContextEngineeringValidationResult(
                    component="Multi_Agent_Coordinator",
                    validation_type="multi_agent_coordination",
                    passed=False,
                    score=0.0,
                    target=1.0,
                    details={"error": str(e)},
                )
            )

    def _generate_validation_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive validation summary."""
        total_validations = len(self.validation_results)
        passed_validations = sum(1 for r in self.validation_results if r.passed)

        # Calculate category scores
        category_scores = {}
        categories = set(r.validation_type for r in self.validation_results)

        for category in categories:
            category_results = [
                r for r in self.validation_results if r.validation_type == category
            ]
            category_score = sum(r.score for r in category_results) / len(
                category_results
            )
            category_scores[category] = category_score

        # Calculate overall score
        overall_score = (
            sum(r.score for r in self.validation_results) / total_validations
            if total_validations > 0
            else 0
        )

        # Determine overall status
        if overall_score >= 0.9:
            status = "excellent"
        elif overall_score >= 0.8:
            status = "good"
        elif overall_score >= 0.7:
            status = "acceptable"
        else:
            status = "needs_improvement"

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "overall_status": status,
            "overall_score": overall_score,
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "validation_time_seconds": total_time,
            "category_scores": category_scores,
            "validation_targets": self.targets,
            "detailed_results": [r.dict() for r in self.validation_results],
        }

        return summary

    def print_validation_summary(self, summary: Dict[str, Any]):
        """Print formatted validation summary."""
        print("\n" + "=" * 80)
        print("🎯 ACGS Context Engineering Validation Summary")
        print("=" * 80)
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Overall Score: {summary['overall_score']:.2f}")
        print(f"Constitutional Hash: {summary['constitutional_hash']}")
        print(f"Total Validations: {summary['total_validations']}")
        print(f"Passed: {summary['passed_validations']}")
        print(f"Failed: {summary['failed_validations']}")
        print(f"Validation Time: {summary['validation_time_seconds']:.2f}s")

        print(f"\n📊 Category Scores:")
        for category, score in summary["category_scores"].items():
            status_icon = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
            print(f"  {status_icon} {category.replace('_', ' ').title()}: {score:.2f}")

        # Show failed validations
        failed_results = [r for r in self.validation_results if not r.passed]
        if failed_results:
            print(f"\n❌ Failed Validations:")
            for result in failed_results:
                print(
                    f"  - {result.component} ({result.validation_type}): {result.score:.2f}/{result.target:.2f}"
                )
        else:
            print(f"\n✅ All validations passed!")

        print("=" * 80)


async def main():
    """Main entry point for ACGS Context Engineering validation."""
    parser = argparse.ArgumentParser(
        description="ACGS Context Engineering Validation Framework"
    )
    parser.add_argument(
        "--base-path", default=".", help="Base path for ACGS repository"
    )
    parser.add_argument(
        "--output-file", help="Output file for validation results (JSON)"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run validation
    validator = ACGSContextEngineeringValidator(args.base_path)
    summary = await validator.run_comprehensive_validation()

    # Print summary
    validator.print_validation_summary(summary)

    # Save results if output file specified
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n📁 Validation results saved to: {args.output_file}")

    # Exit with appropriate code
    if summary["overall_score"] >= 0.8:
        print(f"\n🎉 Context Engineering validation successful!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Context Engineering validation needs improvement")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
