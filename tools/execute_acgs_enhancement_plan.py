#!/usr/bin/env python3
"""
ACGS-1 Enhancement Plan Master Execution Script

This script coordinates the execution of all four enhancement phases:
1. Phase 1: Security & Compliance Audit
2. Phase 2: Test Infrastructure Strengthening
3. Phase 3: Performance Optimization & Monitoring
4. Phase 4: Community & Adoption Strategy

Usage:
    python scripts/execute_acgs_enhancement_plan.py --all-phases
    python scripts/execute_acgs_enhancement_plan.py --phase 1
    python scripts/execute_acgs_enhancement_plan.py --phase 2,3
    python scripts/execute_acgs_enhancement_plan.py --dry-run
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("acgs_enhancement_execution.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class ACGSEnhancementExecutor:
    """Master coordinator for ACGS-1 enhancement plan execution."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.scripts_dir = project_root / "scripts"

        self.execution_results = {
            "execution_id": f"acgs_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "dry_run": dry_run,
            "phases_executed": [],
            "phase_results": {},
            "overall_success": True,
            "recommendations": [],
            "next_steps": [],
        }

        # Define phase configurations
        self.phases = {
            1: {
                "name": "Security & Compliance Audit",
                "script": "phase1_security_audit.py",
                "priority": "CRITICAL",
                "estimated_duration_hours": 8,
                "dependencies": [],
                "success_criteria": [
                    "Zero HIGH/CRITICAL security findings",
                    "Complete license compliance audit",
                    "GPL conflict resolution plan",
                ],
            },
            2: {
                "name": "Test Infrastructure Strengthening",
                "script": "phase2_test_infrastructure.py",
                "priority": "HIGH",
                "estimated_duration_hours": 16,
                "dependencies": [],
                "success_criteria": [
                    "80%+ Anchor program test coverage",
                    "End-to-end workflow testing",
                    "Frontend test infrastructure",
                ],
            },
            3: {
                "name": "Performance Optimization & Monitoring",
                "script": "phase3_performance_optimization.py",
                "priority": "MEDIUM",
                "estimated_duration_hours": 12,
                "dependencies": [2],  # Depends on test infrastructure
                "success_criteria": [
                    "<0.01 SOL per governance action",
                    "<2s LLM response times",
                    "99.9% service uptime monitoring",
                ],
            },
            4: {
                "name": "Community & Adoption Strategy",
                "script": "phase4_community_adoption.py",
                "priority": "MEDIUM",
                "estimated_duration_hours": 10,
                "dependencies": [],
                "success_criteria": [
                    "Technical roadmap published",
                    "15+ good first issues labeled",
                    "Contributor onboarding program",
                ],
            },
        }

    def execute_all_phases(self) -> dict:
        """Execute all enhancement phases in optimal order."""
        logger.info("Starting ACGS-1 enhancement plan execution...")

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No actual changes will be made")

        # Determine execution order based on dependencies
        execution_order = self._calculate_execution_order()
        logger.info(f"Execution order: {execution_order}")

        # Execute phases
        for phase_num in execution_order:
            phase_config = self.phases[phase_num]
            logger.info(f"Starting Phase {phase_num}: {phase_config['name']}")

            start_time = time.time()

            try:
                if self.dry_run:
                    result = self._simulate_phase_execution(phase_num)
                else:
                    result = self._execute_phase(phase_num)

                execution_time = time.time() - start_time
                result["execution_time_seconds"] = execution_time
                result["success"] = True

                self.execution_results["phase_results"][phase_num] = result
                self.execution_results["phases_executed"].append(phase_num)

                logger.info(
                    f"✅ Phase {phase_num} completed successfully in {execution_time:.1f}s"
                )

            except Exception as e:
                execution_time = time.time() - start_time
                error_result = {
                    "success": False,
                    "error": str(e),
                    "execution_time_seconds": execution_time,
                }

                self.execution_results["phase_results"][phase_num] = error_result
                self.execution_results["overall_success"] = False

                logger.error(
                    f"❌ Phase {phase_num} failed after {execution_time:.1f}s: {e}"
                )

                # Decide whether to continue or stop
                if phase_config["priority"] == "CRITICAL":
                    logger.error("Critical phase failed. Stopping execution.")
                    break
                logger.warning(
                    "Non-critical phase failed. Continuing with remaining phases."
                )

        # Generate final report
        self._generate_execution_report()

        # Generate recommendations
        self._generate_recommendations()

        self.execution_results["end_time"] = datetime.now().isoformat()
        return self.execution_results

    def execute_specific_phases(self, phase_numbers: list[int]) -> dict:
        """Execute specific phases only."""
        logger.info(f"Executing specific phases: {phase_numbers}")

        # Validate phase numbers
        invalid_phases = [p for p in phase_numbers if p not in self.phases]
        if invalid_phases:
            raise ValueError(f"Invalid phase numbers: {invalid_phases}")

        # Check dependencies
        for phase_num in phase_numbers:
            dependencies = self.phases[phase_num]["dependencies"]
            missing_deps = [dep for dep in dependencies if dep not in phase_numbers]
            if missing_deps:
                logger.warning(
                    f"Phase {phase_num} has unmet dependencies: {missing_deps}"
                )

        # Execute phases in order
        for phase_num in sorted(phase_numbers):
            phase_config = self.phases[phase_num]
            logger.info(f"Starting Phase {phase_num}: {phase_config['name']}")

            try:
                if self.dry_run:
                    result = self._simulate_phase_execution(phase_num)
                else:
                    result = self._execute_phase(phase_num)

                result["success"] = True
                self.execution_results["phase_results"][phase_num] = result
                self.execution_results["phases_executed"].append(phase_num)

                logger.info(f"✅ Phase {phase_num} completed successfully")

            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                self.execution_results["phase_results"][phase_num] = error_result
                self.execution_results["overall_success"] = False

                logger.error(f"❌ Phase {phase_num} failed: {e}")

        self._generate_execution_report()
        self._generate_recommendations()

        return self.execution_results

    def _calculate_execution_order(self) -> list[int]:
        """Calculate optimal execution order based on dependencies and priorities."""
        # Simple topological sort with priority consideration
        remaining_phases = set(self.phases.keys())
        execution_order = []

        while remaining_phases:
            # Find phases with no unmet dependencies
            ready_phases = []
            for phase_num in remaining_phases:
                dependencies = self.phases[phase_num]["dependencies"]
                if all(dep in execution_order for dep in dependencies):
                    ready_phases.append(phase_num)

            if not ready_phases:
                # Circular dependency or error
                logger.warning(
                    "Circular dependency detected. Using remaining phases in order."
                )
                ready_phases = list(remaining_phases)

            # Sort by priority (CRITICAL > HIGH > MEDIUM > LOW)
            priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            ready_phases.sort(
                key=lambda p: (
                    priority_order.get(self.phases[p]["priority"], 4),
                    p,  # Phase number as tiebreaker
                )
            )

            # Take the highest priority phase
            next_phase = ready_phases[0]
            execution_order.append(next_phase)
            remaining_phases.remove(next_phase)

        return execution_order

    def _execute_phase(self, phase_num: int) -> dict:
        """Execute a specific phase."""
        phase_config = self.phases[phase_num]
        script_path = self.scripts_dir / phase_config["script"]

        if not script_path.exists():
            raise FileNotFoundError(f"Phase script not found: {script_path}")

        # Execute the phase script
        cmd = [
            sys.executable,
            str(script_path),
            "--full-audit" if phase_num == 1 else "--setup-all",
        ]

        logger.info(f"Executing: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            check=False,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=phase_config["estimated_duration_hours"]
            * 3600,  # Convert to seconds
        )

        if result.returncode != 0:
            raise RuntimeError(f"Phase {phase_num} script failed: {result.stderr}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(cmd),
        }

    def _simulate_phase_execution(self, phase_num: int) -> dict:
        """Simulate phase execution for dry run."""
        phase_config = self.phases[phase_num]

        logger.info(f"🔍 SIMULATING Phase {phase_num}: {phase_config['name']}")
        logger.info(f"   Priority: {phase_config['priority']}")
        logger.info(
            f"   Estimated duration: {phase_config['estimated_duration_hours']} hours"
        )
        logger.info(
            f"   Success criteria: {len(phase_config['success_criteria'])} items"
        )

        # Simulate some processing time
        time.sleep(1)

        return {
            "simulated": True,
            "phase_name": phase_config["name"],
            "estimated_duration_hours": phase_config["estimated_duration_hours"],
            "success_criteria": phase_config["success_criteria"],
        }

    def _generate_execution_report(self):
        """Generate comprehensive execution report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"acgs_enhancement_report_{timestamp}.json"

        # Add summary statistics
        total_phases = len(self.phases)
        executed_phases = len(self.execution_results["phases_executed"])
        successful_phases = sum(
            1
            for result in self.execution_results["phase_results"].values()
            if result.get("success", False)
        )

        self.execution_results["summary"] = {
            "total_phases": total_phases,
            "executed_phases": executed_phases,
            "successful_phases": successful_phases,
            "success_rate": (successful_phases / max(1, executed_phases)) * 100,
            "overall_success": self.execution_results["overall_success"],
        }

        # Write report
        with open(report_file, "w") as f:
            json.dump(self.execution_results, f, indent=2)

        logger.info(f"Execution report generated: {report_file}")

        # Print summary
        self._print_execution_summary()

    def _print_execution_summary(self):
        """Print execution summary to console."""
        summary = self.execution_results["summary"]

        print("\n" + "=" * 70)
        print("ACGS-1 ENHANCEMENT PLAN EXECUTION SUMMARY")
        print("=" * 70)

        print("📊 Execution Statistics:")
        print(f"   - Total phases: {summary['total_phases']}")
        print(f"   - Executed phases: {summary['executed_phases']}")
        print(f"   - Successful phases: {summary['successful_phases']}")
        print(f"   - Success rate: {summary['success_rate']:.1f}%")

        print("\n🎯 Phase Results:")
        for phase_num in sorted(self.execution_results["phase_results"].keys()):
            result = self.execution_results["phase_results"][phase_num]
            phase_name = self.phases[phase_num]["name"]
            status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
            duration = result.get("execution_time_seconds", 0)
            print(f"   Phase {phase_num}: {phase_name} - {status} ({duration:.1f}s)")

        if self.execution_results["recommendations"]:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(self.execution_results["recommendations"], 1):
                print(f"   {i}. {rec}")

        if self.execution_results["next_steps"]:
            print("\n🚀 Next Steps:")
            for i, step in enumerate(self.execution_results["next_steps"], 1):
                print(f"   {i}. {step}")

        print("=" * 70)

    def _generate_recommendations(self):
        """Generate recommendations based on execution results."""
        recommendations = []
        next_steps = []

        # Analyze results and generate recommendations
        failed_phases = [
            phase_num
            for phase_num, result in self.execution_results["phase_results"].items()
            if not result.get("success", False)
        ]

        if failed_phases:
            critical_failures = [
                p for p in failed_phases if self.phases[p]["priority"] == "CRITICAL"
            ]

            if critical_failures:
                recommendations.append(
                    f"URGENT: Critical phases {critical_failures} failed. "
                    "Address these issues before proceeding with deployment."
                )
                next_steps.append("Review and fix critical phase failures")

            if len(failed_phases) > len(critical_failures):
                non_critical_failures = [
                    p for p in failed_phases if p not in critical_failures
                ]
                recommendations.append(
                    f"Non-critical phases {non_critical_failures} failed. "
                    "Consider re-running these phases after addressing root causes."
                )

        # Success-based recommendations
        successful_phases = [
            phase_num
            for phase_num, result in self.execution_results["phase_results"].items()
            if result.get("success", False)
        ]

        if 1 in successful_phases:
            next_steps.append("Review security audit results and implement fixes")

        if 2 in successful_phases:
            next_steps.append("Run comprehensive test suite to validate coverage")

        if 3 in successful_phases:
            next_steps.append("Monitor performance metrics and adjust SLOs")

        if 4 in successful_phases:
            next_steps.append("Launch community onboarding program")

        # General recommendations
        if self.execution_results["overall_success"]:
            recommendations.extend(
                [
                    "All phases completed successfully. Ready for production deployment.",
                    "Establish regular monitoring and maintenance schedules.",
                    "Plan for Phase 5: Advanced Blockchain Integration.",
                ]
            )
            next_steps.extend(
                [
                    "Deploy to Solana mainnet",
                    "Launch community governance program",
                    "Begin Phase 5 development planning",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Address failed phases before production deployment.",
                    "Consider running phases in smaller increments.",
                    "Increase monitoring and validation during execution.",
                ]
            )

        self.execution_results["recommendations"] = recommendations
        self.execution_results["next_steps"] = next_steps


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ACGS-1 Enhancement Plan Executor")
    parser.add_argument(
        "--all-phases", action="store_true", help="Execute all enhancement phases"
    )
    parser.add_argument(
        "--phase",
        type=str,
        help='Execute specific phases (comma-separated, e.g., "1,2,3")',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without making changes",
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )

    args = parser.parse_args()

    # Initialize executor
    executor = ACGSEnhancementExecutor(args.project_root, args.dry_run)

    try:
        if args.all_phases or (not args.phase):
            results = executor.execute_all_phases()
        else:
            # Parse phase numbers
            phase_numbers = [int(p.strip()) for p in args.phase.split(",")]
            results = executor.execute_specific_phases(phase_numbers)

        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)

    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
