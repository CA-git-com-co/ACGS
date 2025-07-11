#!/usr/bin/env python3
"""
ACGS-1 Enhancement Readiness Validation Script

This script validates the current state of the ACGS-1 codebase and determines
readiness for enhancement plan execution. It checks:

1. Quantumagi deployment status and functionality
2. Codebase structure and organization
3. Dependencies and environment setup
4. CI/CD pipeline status
5. Test infrastructure baseline

Usage:
    python scripts/validate_enhancement_readiness.py
    python scripts/validate_enhancement_readiness.py --detailed
    python scripts/validate_enhancement_readiness.py --fix-issues
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhancement_readiness_validation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EnhancementReadinessValidator:
    """Validates ACGS-1 readiness for enhancement plan execution."""

    def __init__(self, project_root: Path, fix_issues: bool = False):
        self.project_root = project_root
        self.fix_issues = fix_issues

        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_readiness": False,
            "readiness_score": 0.0,
            "validations": {
                "quantumagi_status": {},
                "codebase_structure": {},
                "dependencies": {},
                "ci_cd_pipeline": {},
                "test_infrastructure": {},
            },
            "issues_found": [],
            "recommendations": [],
            "enhancement_plan_readiness": {},
        }

    def validate_all(self) -> dict:
        """Run comprehensive readiness validation."""
        logger.info("Starting ACGS-1 enhancement readiness validation...")

        # Run all validation checks
        validations = [
            ("quantumagi_status", self._validate_quantumagi_deployment),
            ("codebase_structure", self._validate_codebase_structure),
            ("dependencies", self._validate_dependencies),
            ("ci_cd_pipeline", self._validate_ci_cd_pipeline),
            ("test_infrastructure", self._validate_test_infrastructure),
        ]

        total_score = 0.0
        max_score = len(validations) * 100.0

        for validation_name, validation_func in validations:
            logger.info(f"Running {validation_name} validation...")

            try:
                result = validation_func()
                self.validation_results["validations"][validation_name] = result
                total_score += result.get("score", 0)

                if result.get("issues"):
                    self.validation_results["issues_found"].extend(result["issues"])

                status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
                score = result.get("score", 0)
                logger.info(f"{validation_name}: {status} (Score: {score}/100)")

            except Exception as e:
                logger.error(f"Validation {validation_name} failed: {e}")
                self.validation_results["validations"][validation_name] = {
                    "passed": False,
                    "score": 0,
                    "error": str(e),
                }

        # Calculate overall readiness
        self.validation_results["readiness_score"] = (total_score / max_score) * 100
        self.validation_results["overall_readiness"] = (
            self.validation_results["readiness_score"] >= 80.0
        )

        # Generate recommendations
        self._generate_recommendations()

        # Assess enhancement plan readiness
        self._assess_enhancement_plan_readiness()

        # Generate report
        self._generate_readiness_report()

        return self.validation_results

    def _validate_quantumagi_deployment(self) -> dict:
        """Validate Quantumagi deployment status and functionality."""
        result = {"passed": False, "score": 0, "checks": {}, "issues": []}

        # Check deployment status file
        deployment_status_file = self.project_root / "QUANTUMAGI_DEPLOYMENT_STATUS.md"
        if deployment_status_file.exists():
            result["checks"]["deployment_status_file"] = True
            result["score"] += 20
        else:
            result["issues"].append("Quantumagi deployment status file not found")

        # Check blockchain directory structure
        blockchain_dir = self.project_root / "blockchain"
        if blockchain_dir.exists():
            result["checks"]["blockchain_directory"] = True
            result["score"] += 15

            # Check for programs
            programs_dir = blockchain_dir / "programs"
            if programs_dir.exists():
                programs = list(programs_dir.iterdir())
                expected_programs = ["quantumagi-core", "appeals", "logging"]

                found_programs = [p.name for p in programs if p.is_dir()]
                missing_programs = [
                    p for p in expected_programs if p not in found_programs
                ]

                if not missing_programs:
                    result["checks"]["required_programs"] = True
                    result["score"] += 25
                else:
                    result["issues"].append(f"Missing programs: {missing_programs}")
            else:
                result["issues"].append("Programs directory not found")
        else:
            result["issues"].append("Blockchain directory not found")

        # Check for compiled artifacts
        target_dir = blockchain_dir / "target"
        if target_dir.exists():
            idl_dir = target_dir / "idl"
            deploy_dir = target_dir / "deploy"

            if idl_dir.exists() and deploy_dir.exists():
                result["checks"]["compiled_artifacts"] = True
                result["score"] += 20
            else:
                result["issues"].append("Missing compiled artifacts (IDL or deploy)")
        else:
            result["issues"].append(
                "Target directory not found - programs not compiled"
            )

        # Check test results
        test_files = list(blockchain_dir.glob("**/test*.json"))
        if test_files:
            result["checks"]["test_results"] = True
            result["score"] += 20
        else:
            result["issues"].append("No test result files found")

        result["passed"] = result["score"] >= 80
        return result

    def _validate_codebase_structure(self) -> dict:
        """Validate codebase structure and organization."""
        result = {"passed": False, "score": 0, "checks": {}, "issues": []}

        # Check main directories
        expected_dirs = [
            "blockchain",
            "services",
            "applications",
            "tests",
            "docs",
            "scripts",
        ]

        missing_dirs = []
        for dir_name in expected_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                result["checks"][f"{dir_name}_directory"] = True
                result["score"] += 15
            else:
                missing_dirs.append(dir_name)

        if missing_dirs:
            result["issues"].append(f"Missing directories: {missing_dirs}")

        # Check services structure
        services_dir = self.project_root / "services"
        if services_dir.exists():
            expected_service_dirs = ["core", "platform", "research"]
            service_subdirs = [d.name for d in services_dir.iterdir() if d.is_dir()]

            missing_service_dirs = [
                d for d in expected_service_dirs if d not in service_subdirs
            ]
            if not missing_service_dirs:
                result["checks"]["services_structure"] = True
                result["score"] += 10
            else:
                result["issues"].append(
                    f"Missing service directories: {missing_service_dirs}"
                )

        result["passed"] = result["score"] >= 80
        return result

    def _validate_dependencies(self) -> dict:
        """Validate dependencies and environment setup."""
        result = {"passed": False, "score": 0, "checks": {}, "issues": []}

        # Check for requirements files
        requirements_files = list(self.project_root.glob("**/requirements*.txt"))
        if requirements_files:
            result["checks"]["requirements_files"] = True
            result["score"] += 20
            result["requirements_count"] = len(requirements_files)
        else:
            result["issues"].append("No requirements.txt files found")

        # Check Python environment
        try:
            python_version = subprocess.run(
                [sys.executable, "--version"],
                check=False,
                capture_output=True,
                text=True,
            ).stdout.strip()

            if "Python 3." in python_version:
                result["checks"]["python_version"] = True
                result["score"] += 15
                result["python_version"] = python_version
            else:
                result["issues"].append(f"Invalid Python version: {python_version}")
        except Exception as e:
            result["issues"].append(f"Could not check Python version: {e}")

        # Check Node.js environment
        try:
            node_version = subprocess.run(
                ["node", "--version"], check=False, capture_output=True, text=True
            ).stdout.strip()

            if node_version.startswith("v"):
                result["checks"]["node_version"] = True
                result["score"] += 15
                result["node_version"] = node_version
            else:
                result["issues"].append(f"Invalid Node.js version: {node_version}")
        except Exception as e:
            result["issues"].append(f"Node.js not found: {e}")

        # Check Solana CLI
        try:
            solana_version = subprocess.run(
                ["solana", "--version"], check=False, capture_output=True, text=True
            ).stdout.strip()

            if "solana-cli" in solana_version:
                result["checks"]["solana_cli"] = True
                result["score"] += 25
                result["solana_version"] = solana_version
            else:
                result["issues"].append(f"Invalid Solana CLI version: {solana_version}")
        except Exception as e:
            result["issues"].append(f"Solana CLI not found: {e}")

        # Check Anchor
        try:
            anchor_version = subprocess.run(
                ["anchor", "--version"], check=False, capture_output=True, text=True
            ).stdout.strip()

            if "anchor-cli" in anchor_version:
                result["checks"]["anchor_cli"] = True
                result["score"] += 25
                result["anchor_version"] = anchor_version
            else:
                result["issues"].append(f"Invalid Anchor version: {anchor_version}")
        except Exception as e:
            result["issues"].append(f"Anchor CLI not found: {e}")

        result["passed"] = result["score"] >= 80
        return result

    def _validate_ci_cd_pipeline(self) -> dict:
        """Validate CI/CD pipeline configuration."""
        result = {"passed": False, "score": 0, "checks": {}, "issues": []}

        # Check GitHub workflows
        github_dir = self.project_root / ".github"
        workflows_dir = github_dir / "workflows"

        if workflows_dir.exists():
            result["checks"]["workflows_directory"] = True
            result["score"] += 20

            # Check for CI workflow
            ci_workflow = workflows_dir / "ci.yml"
            if ci_workflow.exists():
                result["checks"]["ci_workflow"] = True
                result["score"] += 30

                # Check workflow content
                with open(ci_workflow) as f:
                    content = f.read()

                    if "security_scan" in content:
                        result["checks"]["security_scanning"] = True
                        result["score"] += 15
                    else:
                        result["issues"].append("CI workflow missing security scanning")

                    if "unit_tests" in content:
                        result["checks"]["unit_testing"] = True
                        result["score"] += 15
                    else:
                        result["issues"].append("CI workflow missing unit testing")

                    if "build_images" in content:
                        result["checks"]["docker_builds"] = True
                        result["score"] += 10
                    else:
                        result["issues"].append("CI workflow missing Docker builds")
            else:
                result["issues"].append("CI workflow file not found")
        else:
            result["issues"].append("GitHub workflows directory not found")

        # Check for other important workflows
        expected_workflows = ["codeql.yml", "defender-for-devops.yml"]
        for workflow in expected_workflows:
            workflow_file = workflows_dir / workflow
            if workflow_file.exists():
                result["checks"][f"{workflow}_exists"] = True
                result["score"] += 5

        result["passed"] = result["score"] >= 80
        return result

    def _validate_test_infrastructure(self) -> dict:
        """Validate test infrastructure and coverage."""
        result = {"passed": False, "score": 0, "checks": {}, "issues": []}

        # Check tests directory
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            result["checks"]["tests_directory"] = True
            result["score"] += 20

            # Check test subdirectories
            expected_test_dirs = ["unit", "integration", "e2e"]
            test_subdirs = [d.name for d in tests_dir.iterdir() if d.is_dir()]

            for test_dir in expected_test_dirs:
                if test_dir in test_subdirs:
                    result["checks"][f"{test_dir}_tests"] = True
                    result["score"] += 15
                else:
                    result["issues"].append(f"Missing {test_dir} tests directory")
        else:
            result["issues"].append("Tests directory not found")

        # Check Anchor tests
        blockchain_tests = self.project_root / "blockchain" / "tests"
        if blockchain_tests.exists():
            test_files = list(blockchain_tests.glob("*.ts"))
            if test_files:
                result["checks"]["anchor_tests"] = True
                result["score"] += 25
                result["anchor_test_count"] = len(test_files)
            else:
                result["issues"].append("No Anchor test files found")
        else:
            result["issues"].append("Blockchain tests directory not found")

        # Check pytest configuration
        pytest_config = self.project_root / "pytest.ini"
        if pytest_config.exists():
            result["checks"]["pytest_config"] = True
            result["score"] += 10
        else:
            result["issues"].append("pytest.ini configuration not found")

        result["passed"] = result["score"] >= 70  # Lower threshold for tests
        return result

    def _generate_recommendations(self):
        """Generate recommendations based on validation results."""
        recommendations = []

        # Analyze validation results
        for validation_name, validation_result in self.validation_results[
            "validations"
        ].items():
            if not validation_result.get("passed", False):
                score = validation_result.get("score", 0)

                if validation_name == "quantumagi_status" and score < 80:
                    recommendations.append(
                        "CRITICAL: Quantumagi deployment validation failed. "
                        "Ensure Quantumagi is properly deployed before running enhancement plan."
                    )

                elif validation_name == "dependencies" and score < 80:
                    recommendations.append(
                        "HIGH: Dependency validation failed. "
                        "Install required tools (Solana CLI, Anchor, Node.js) before proceeding."
                    )

                elif validation_name == "ci_cd_pipeline" and score < 80:
                    recommendations.append(
                        "MEDIUM: CI/CD pipeline validation failed. "
                        "Fix workflow configurations to ensure proper automation."
                    )

        # General recommendations
        if self.validation_results["readiness_score"] < 80:
            recommendations.append(
                "Overall readiness score is below 80%. "
                "Address critical issues before running enhancement plan."
            )

        if self.validation_results["issues_found"]:
            recommendations.append(
                f"Found {len(self.validation_results['issues_found'])} issues. "
                "Review and fix these issues to improve readiness."
            )

        self.validation_results["recommendations"] = recommendations

    def _assess_enhancement_plan_readiness(self):
        """Assess readiness for each enhancement phase."""
        phase_readiness = {}

        # Phase 1: Security & Compliance Audit
        phase_1_ready = (
            self.validation_results["validations"]["dependencies"].get("score", 0) >= 60
            and len(self.validation_results["issues_found"]) < 10
        )
        phase_readiness[1] = {
            "ready": phase_1_ready,
            "requirements_met": phase_1_ready,
            "blocking_issues": (
                []
                if phase_1_ready
                else ["Dependency issues", "Too many validation failures"]
            ),
        }

        # Phase 2: Test Infrastructure
        phase_2_ready = (
            self.validation_results["validations"]["quantumagi_status"].get("score", 0)
            >= 80
            and self.validation_results["validations"]["test_infrastructure"].get(
                "score", 0
            )
            >= 50
        )
        phase_readiness[2] = {
            "ready": phase_2_ready,
            "requirements_met": phase_2_ready,
            "blocking_issues": (
                []
                if phase_2_ready
                else ["Quantumagi not ready", "Test infrastructure incomplete"]
            ),
        }

        # Phase 3: Performance Optimization
        phase_3_ready = phase_2_ready  # Depends on Phase 2
        phase_readiness[3] = {
            "ready": phase_3_ready,
            "requirements_met": phase_3_ready,
            "blocking_issues": (
                [] if phase_3_ready else ["Phase 2 requirements not met"]
            ),
        }

        # Phase 4: Community Adoption
        phase_4_ready = (
            self.validation_results["validations"]["codebase_structure"].get("score", 0)
            >= 70
            and self.validation_results["validations"]["ci_cd_pipeline"].get("score", 0)
            >= 60
        )
        phase_readiness[4] = {
            "ready": phase_4_ready,
            "requirements_met": phase_4_ready,
            "blocking_issues": (
                []
                if phase_4_ready
                else ["Codebase structure issues", "CI/CD pipeline issues"]
            ),
        }

        self.validation_results["enhancement_plan_readiness"] = phase_readiness

    def _generate_readiness_report(self):
        """Generate comprehensive readiness report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = (
            self.project_root / f"enhancement_readiness_report_{timestamp}.json"
        )

        with open(report_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        logger.info(f"Readiness report generated: {report_file}")

        # Print summary
        self._print_readiness_summary()

    def _print_readiness_summary(self):
        """Print readiness summary to console."""
        print("\n" + "=" * 70)
        print("ACGS-1 ENHANCEMENT READINESS VALIDATION SUMMARY")
        print("=" * 70)

        # Overall readiness
        score = self.validation_results["readiness_score"]
        status = (
            "✅ READY"
            if self.validation_results["overall_readiness"]
            else "❌ NOT READY"
        )
        print(f"🎯 Overall Readiness: {status} (Score: {score:.1f}/100)")

        # Individual validations
        print("\n📊 Validation Results:")
        for name, result in self.validation_results["validations"].items():
            score = result.get("score", 0)
            status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
            print(f"   {name.replace('_', ' ').title()}: {status} ({score}/100)")

        # Issues found
        issues = self.validation_results["issues_found"]
        if issues:
            print(f"\n⚠️ Issues Found ({len(issues)}):")
            for i, issue in enumerate(issues[:10], 1):  # Show first 10 issues
                print(f"   {i}. {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")

        # Phase readiness
        print("\n🚀 Enhancement Phase Readiness:")
        for phase_num, readiness in self.validation_results[
            "enhancement_plan_readiness"
        ].items():
            status = "✅ READY" if readiness["ready"] else "❌ NOT READY"
            print(f"   Phase {phase_num}: {status}")
            if readiness["blocking_issues"]:
                for issue in readiness["blocking_issues"]:
                    print(f"      - {issue}")

        # Recommendations
        recommendations = self.validation_results["recommendations"]
        if recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

        print("=" * 70)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="ACGS-1 Enhancement Readiness Validator"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Run detailed validation with extended checks",
    )
    parser.add_argument(
        "--fix-issues", action="store_true", help="Attempt to fix issues automatically"
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = EnhancementReadinessValidator(args.project_root, args.fix_issues)

    try:
        results = validator.validate_all()

        # Exit with appropriate code
        sys.exit(0 if results["overall_readiness"] else 1)

    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
