#!/usr/bin/env python3
"""
ACGS Chaos Experiments Orchestrator
Orchestrates and manages chaos engineering experiments for ACGS system validation.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add the infrastructure chaos path to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent / "infrastructure/chaos"))

from acgs_chaos_framework import (
    ACGSChaosFramework,
    ChaosExperiment,
    ChaosType,
    ExperimentStatus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ChaosExperimentOrchestrator:
    """Orchestrates chaos engineering experiments for ACGS."""

    def __init__(self):
        self.framework = ACGSChaosFramework()
        self.experiment_suites = self.define_experiment_suites()

    def define_experiment_suites(self) -> dict:
        """Define predefined experiment suites."""
        return {
            "basic_resilience": [
                {
                    "name": "Auth Service Failure Test",
                    "chaos_type": "service_failure",
                    "target_services": ["auth-service"],
                    "duration_seconds": 60,
                    "intensity": 1.0,
                    "blast_radius": "single_service",
                    "steady_state_hypothesis": {
                        "auth_service_available": True,
                        "constitutional_compliance": ">95%",
                    },
                },
                {
                    "name": "Network Latency Test",
                    "chaos_type": "network_latency",
                    "target_services": ["ac-service", "pgc-service"],
                    "duration_seconds": 120,
                    "intensity": 0.3,
                    "blast_radius": "service_group",
                },
                {
                    "name": "Database Connection Failure",
                    "chaos_type": "database_failure",
                    "target_services": ["auth-service", "ac-service"],
                    "duration_seconds": 90,
                    "intensity": 1.0,
                    "blast_radius": "service_group",
                },
            ],
            "constitutional_compliance": [
                {
                    "name": "Constitutional Validation Failure",
                    "chaos_type": "constitutional_validation_failure",
                    "target_services": ["ac-service", "pgc-service", "ec-service"],
                    "duration_seconds": 180,
                    "intensity": 0.5,
                    "blast_radius": "service_group",
                    "constitutional_compliance_required": True,
                },
                {
                    "name": "AC Service Under Load",
                    "chaos_type": "resource_exhaustion",
                    "target_services": ["ac-service"],
                    "duration_seconds": 300,
                    "intensity": 0.7,
                    "blast_radius": "single_service",
                },
            ],
            "message_broker_resilience": [
                {
                    "name": "NATS Broker Failure",
                    "chaos_type": "message_broker_failure",
                    "target_services": ["ec-service", "pgc-service"],
                    "duration_seconds": 120,
                    "intensity": 1.0,
                    "blast_radius": "service_group",
                },
                {
                    "name": "Network Partition Between Services",
                    "chaos_type": "network_partition",
                    "target_services": ["ec-service", "ac-service"],
                    "duration_seconds": 150,
                    "intensity": 0.8,
                    "blast_radius": "service_group",
                },
            ],
            "resource_stress": [
                {
                    "name": "System Memory Pressure",
                    "chaos_type": "memory_pressure",
                    "target_services": ["auth-service", "ac-service", "ec-service"],
                    "duration_seconds": 240,
                    "intensity": 0.6,
                    "blast_radius": "system_wide",
                    "max_impact_threshold": 0.15,
                },
                {
                    "name": "CPU Stress Test",
                    "chaos_type": "cpu_stress",
                    "target_services": ["fv-service", "gs-service"],
                    "duration_seconds": 180,
                    "intensity": 0.8,
                    "blast_radius": "service_group",
                },
            ],
            "comprehensive_failure": [
                {
                    "name": "Multi-Service Cascade Failure",
                    "chaos_type": "service_failure",
                    "target_services": ["integrity-service", "fv-service"],
                    "duration_seconds": 300,
                    "intensity": 1.0,
                    "blast_radius": "service_group",
                },
                {
                    "name": "Infrastructure Stress Test",
                    "chaos_type": "resource_exhaustion",
                    "target_services": [
                        "auth-service",
                        "ac-service",
                        "pgc-service",
                        "ec-service",
                    ],
                    "duration_seconds": 600,
                    "intensity": 0.4,
                    "blast_radius": "system_wide",
                    "max_impact_threshold": 0.2,
                },
            ],
        }

    async def run_experiment_suite(self, suite_name: str) -> dict:
        """Run a complete experiment suite."""
        logger.info(f"Running chaos experiment suite: {suite_name}")

        if suite_name not in self.experiment_suites:
            raise ValueError(f"Unknown experiment suite: {suite_name}")

        suite_experiments = self.experiment_suites[suite_name]
        results = {
            "suite_name": suite_name,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "experiments": [],
            "summary": {
                "total_experiments": len(suite_experiments),
                "successful_experiments": 0,
                "failed_experiments": 0,
                "aborted_experiments": 0,
            },
        }

        # Initialize framework
        await self.framework.start_framework()

        # Wait for system to stabilize
        await asyncio.sleep(10)

        for experiment_config in suite_experiments:
            try:
                logger.info(f"Starting experiment: {experiment_config['name']}")

                # Create experiment
                experiment = await self.framework.create_experiment(experiment_config)

                # Execute experiment
                success = await self.framework.execute_experiment(experiment)

                # Record results
                experiment_result = {
                    "experiment_id": experiment.experiment_id,
                    "name": experiment.name,
                    "chaos_type": experiment.chaos_type.value,
                    "target_services": experiment.target_services,
                    "status": experiment.status.value,
                    "start_time": (
                        experiment.start_time.isoformat()
                        if experiment.start_time
                        else None
                    ),
                    "end_time": (
                        experiment.end_time.isoformat() if experiment.end_time else None
                    ),
                    "duration_seconds": (
                        (experiment.end_time - experiment.start_time).total_seconds()
                        if experiment.start_time and experiment.end_time
                        else 0
                    ),
                    "success": success,
                    "results": experiment.results,
                }

                results["experiments"].append(experiment_result)

                # Update summary
                if experiment.status == ExperimentStatus.COMPLETED:
                    results["summary"]["successful_experiments"] += 1
                elif experiment.status == ExperimentStatus.FAILED:
                    results["summary"]["failed_experiments"] += 1
                elif experiment.status == ExperimentStatus.ABORTED:
                    results["summary"]["aborted_experiments"] += 1

                # Wait between experiments
                logger.info(f"Waiting 30 seconds before next experiment...")
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Experiment {experiment_config['name']} failed: {e}")
                results["summary"]["failed_experiments"] += 1

        results["end_time"] = datetime.now(timezone.utc).isoformat()
        results["constitutional_hash"] = CONSTITUTIONAL_HASH

        # Save results
        await self.save_experiment_results(results)

        logger.info(f"Completed chaos experiment suite: {suite_name}")
        return results

    async def run_single_experiment(self, experiment_config: dict) -> dict:
        """Run a single chaos experiment."""
        logger.info(f"Running single chaos experiment: {experiment_config['name']}")

        # Initialize framework
        await self.framework.start_framework()

        # Wait for system to stabilize
        await asyncio.sleep(10)

        try:
            # Create experiment
            experiment = await self.framework.create_experiment(experiment_config)

            # Execute experiment
            success = await self.framework.execute_experiment(experiment)

            # Prepare results
            result = {
                "experiment_id": experiment.experiment_id,
                "name": experiment.name,
                "chaos_type": experiment.chaos_type.value,
                "target_services": experiment.target_services,
                "status": experiment.status.value,
                "start_time": (
                    experiment.start_time.isoformat() if experiment.start_time else None
                ),
                "end_time": (
                    experiment.end_time.isoformat() if experiment.end_time else None
                ),
                "duration_seconds": (
                    (experiment.end_time - experiment.start_time).total_seconds()
                    if experiment.start_time and experiment.end_time
                    else 0
                ),
                "success": success,
                "results": experiment.results,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            # Save results
            await self.save_experiment_results({"single_experiment": result})

            return result

        except Exception as e:
            logger.error(f"Single experiment failed: {e}")
            return {
                "name": experiment_config["name"],
                "status": "failed",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

    async def validate_system_resilience(self) -> dict:
        """Run comprehensive system resilience validation."""
        logger.info("Starting comprehensive system resilience validation...")

        validation_results = {
            "validation_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "suite_results": {},
            "overall_summary": {
                "total_suites": 0,
                "successful_suites": 0,
                "total_experiments": 0,
                "successful_experiments": 0,
                "system_resilience_score": 0.0,
            },
        }

        # Run all experiment suites
        for suite_name in self.experiment_suites.keys():
            try:
                logger.info(f"Running validation suite: {suite_name}")
                suite_result = await self.run_experiment_suite(suite_name)
                validation_results["suite_results"][suite_name] = suite_result

                # Update overall summary
                validation_results["overall_summary"]["total_suites"] += 1
                validation_results["overall_summary"][
                    "total_experiments"
                ] += suite_result["summary"]["total_experiments"]
                validation_results["overall_summary"][
                    "successful_experiments"
                ] += suite_result["summary"]["successful_experiments"]

                if (
                    suite_result["summary"]["successful_experiments"]
                    == suite_result["summary"]["total_experiments"]
                ):
                    validation_results["overall_summary"]["successful_suites"] += 1

                # Wait between suites
                logger.info("Waiting 60 seconds before next suite...")
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Validation suite {suite_name} failed: {e}")

        # Calculate resilience score
        total_experiments = validation_results["overall_summary"]["total_experiments"]
        successful_experiments = validation_results["overall_summary"][
            "successful_experiments"
        ]

        if total_experiments > 0:
            resilience_score = (successful_experiments / total_experiments) * 100
            validation_results["overall_summary"][
                "system_resilience_score"
            ] = resilience_score

        validation_results["validation_end"] = datetime.now(timezone.utc).isoformat()

        # Save comprehensive results
        await self.save_experiment_results(
            validation_results, "comprehensive_validation"
        )

        logger.info(
            f"System resilience validation completed. Score: {resilience_score:.1f}%"
        )
        return validation_results

    async def save_experiment_results(
        self, results: dict, result_type: str = "experiment"
    ):
        """Save experiment results to file."""
        # Create results directory
        results_dir = Path("reports/chaos_experiments")
        results_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result_type}_results_{timestamp}.json"

        # Save results
        results_file = results_dir / filename
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Experiment results saved: {results_file}")

    def get_available_suites(self) -> list:
        """Get list of available experiment suites."""
        return list(self.experiment_suites.keys())

    def get_suite_details(self, suite_name: str) -> dict:
        """Get details of a specific experiment suite."""
        if suite_name not in self.experiment_suites:
            return {}

        suite = self.experiment_suites[suite_name]
        return {
            "suite_name": suite_name,
            "experiment_count": len(suite),
            "experiments": [
                {
                    "name": exp["name"],
                    "chaos_type": exp["chaos_type"],
                    "target_services": exp["target_services"],
                    "duration_seconds": exp["duration_seconds"],
                    "blast_radius": exp["blast_radius"],
                }
                for exp in suite
            ],
        }


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS Chaos Engineering Orchestrator")
    parser.add_argument(
        "--suite",
        choices=[
            "basic_resilience",
            "constitutional_compliance",
            "message_broker_resilience",
            "resource_stress",
            "comprehensive_failure",
            "all",
        ],
        help="Experiment suite to run",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run comprehensive system resilience validation",
    )
    parser.add_argument(
        "--list-suites", action="store_true", help="List available experiment suites"
    )
    parser.add_argument(
        "--suite-details", type=str, help="Show details of a specific suite"
    )

    args = parser.parse_args()

    orchestrator = ChaosExperimentOrchestrator()

    try:
        if args.list_suites:
            suites = orchestrator.get_available_suites()
            print("Available experiment suites:")
            for suite in suites:
                print(f"  - {suite}")
            return

        if args.suite_details:
            details = orchestrator.get_suite_details(args.suite_details)
            if details:
                print(json.dumps(details, indent=2))
            else:
                print(f"Suite '{args.suite_details}' not found")
            return

        if args.validate:
            results = await orchestrator.validate_system_resilience()

            print("\n" + "=" * 60)
            print("ACGS SYSTEM RESILIENCE VALIDATION RESULTS")
            print("=" * 60)
            print(f"Total Suites: {results['overall_summary']['total_suites']}")
            print(
                f"Successful Suites: {results['overall_summary']['successful_suites']}"
            )
            print(
                f"Total Experiments: {results['overall_summary']['total_experiments']}"
            )
            print(
                f"Successful Experiments: {results['overall_summary']['successful_experiments']}"
            )
            print(
                f"System Resilience Score: {results['overall_summary']['system_resilience_score']:.1f}%"
            )
            print(f"Constitutional Hash: {results['constitutional_hash']}")
            print("=" * 60)

        elif args.suite:
            if args.suite == "all":
                # Run all suites
                for suite_name in orchestrator.get_available_suites():
                    results = await orchestrator.run_experiment_suite(suite_name)
                    print(f"\nSuite '{suite_name}' completed:")
                    print(
                        f"  Successful: {results['summary']['successful_experiments']}"
                    )
                    print(f"  Failed: {results['summary']['failed_experiments']}")
                    print(f"  Aborted: {results['summary']['aborted_experiments']}")
            else:
                results = await orchestrator.run_experiment_suite(args.suite)

                print("\n" + "=" * 60)
                print(f"CHAOS EXPERIMENT SUITE RESULTS: {args.suite}")
                print("=" * 60)
                print(f"Total Experiments: {results['summary']['total_experiments']}")
                print(f"Successful: {results['summary']['successful_experiments']}")
                print(f"Failed: {results['summary']['failed_experiments']}")
                print(f"Aborted: {results['summary']['aborted_experiments']}")
                print(f"Constitutional Hash: {results['constitutional_hash']}")
                print("=" * 60)
        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Chaos experiment orchestration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
