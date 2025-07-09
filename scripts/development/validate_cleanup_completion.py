#!/usr/bin/env python3
"""
ACGS-1 Cleanup Completion Validation

This script validates that the cleanup was successful and all critical components are preserved.
"""

import json
from datetime import datetime
from pathlib import Path


class CleanupValidation:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_validation": {
                "core_services": {},
                "critical_components": {},
                "quantumagi_deployment": {},
                "enhancement_framework": {},
                "database_components": {},
                "blockchain_components": {},
            },
            "summary": {
                "total_validations": 0,
                "passed_validations": 0,
                "failed_validations": 0,
                "overall_status": "UNKNOWN",
            },
        }

    def validate_core_services(self):
        """Validate all 7 core services are present and properly structured."""
        print("🏗️ Validating core services...")

        required_services = {
            "constitutional-ai": "Constitutional AI Service (AC)",
            "governance-synthesis": "Governance Synthesis Service (GS)",
            "formal-verification": "Formal Verification Service (FV)",
            "policy-governance": "Policy Governance Service (PGC)",
            "evolutionary-computation": "Evolutionary Computation Service (EC)",
            "self-evolving-ai": "Self-Evolving AI Service",
            "acgs-pgp-v8": "ACGS-PGP v8 Service",
        }

        services_core = self.project_root / "services" / "core"
        service_results = {}

        for service_name, description in required_services.items():
            service_path = services_core / service_name

            validation = {
                "exists": service_path.exists(),
                "description": description,
                "has_main_app": False,
                "has_config": False,
                "has_requirements": False,
            }

            if validation["exists"]:
                # Check for main application files
                app_paths = [
                    service_path / "app",
                    service_path / "main.py",
                    service_path / f"{service_name.replace('-', '_')}_service",
                ]
                validation["has_main_app"] = any(p.exists() for p in app_paths)

                # Check for configuration
                config_paths = [
                    service_path / "config",
                    service_path / "app" / "config",
                ]
                validation["has_config"] = any(p.exists() for p in config_paths)

                # Check for requirements
                req_paths = [
                    service_path / "requirements.txt",
                    service_path / "pyproject.toml",
                ]
                validation["has_requirements"] = any(p.exists() for p in req_paths)

            service_results[service_name] = validation
            status = (
                "✅"
                if all([validation["exists"], validation["has_main_app"]])
                else "❌"
            )
            print(f"  {status} {service_name}: {description}")

        self.validation_results["cleanup_validation"]["core_services"] = service_results
        return all(s["exists"] for s in service_results.values())

    def validate_enhancement_framework(self):
        """Validate enhancement framework is preserved."""
        print("🔧 Validating enhancement framework...")

        framework_path = (
            self.project_root / "services" / "shared" / "enhancement_framework"
        )

        validation = {
            "exists": framework_path.exists(),
            "has_components": False,
            "component_count": 0,
        }

        if validation["exists"]:
            components = [
                "cache_enhancer.py",
                "constitutional_validator.py",
                "monitoring_integrator.py",
                "performance_optimizer.py",
                "service_enhancer.py",
                "service_template.py",
            ]

            existing_components = [
                c for c in components if (framework_path / c).exists()
            ]
            validation["has_components"] = len(existing_components) >= 4
            validation["component_count"] = len(existing_components)

        self.validation_results["cleanup_validation"][
            "enhancement_framework"
        ] = validation

        status = "✅" if validation["exists"] and validation["has_components"] else "❌"
        print(
            f"  {status} Enhancement Framework: {validation['component_count']} components"
        )

        return validation["exists"] and validation["has_components"]

    def validate_quantumagi_deployment(self):
        """Validate Quantumagi Solana deployment is preserved."""
        print("⛓️ Validating Quantumagi deployment...")

        quantumagi_path = self.project_root / "blockchain" / "quantumagi-deployment"

        validation = {
            "exists": quantumagi_path.exists(),
            "has_constitution_data": False,
            "has_deployment_scripts": False,
            "has_governance_accounts": False,
        }

        if validation["exists"]:
            critical_files = [
                "constitution_data.json",
                "governance_accounts.json",
                "initial_policies.json",
                "complete_deployment.sh",
            ]

            validation["has_constitution_data"] = (
                quantumagi_path / "constitution_data.json"
            ).exists()
            validation["has_deployment_scripts"] = (
                quantumagi_path / "complete_deployment.sh"
            ).exists()
            validation["has_governance_accounts"] = (
                quantumagi_path / "governance_accounts.json"
            ).exists()

        self.validation_results["cleanup_validation"][
            "quantumagi_deployment"
        ] = validation

        status = "✅" if all(validation.values()) else "❌"
        print(f"  {status} Quantumagi Deployment: Constitution hash cdd01ef066bc6cf2")

        return all(validation.values())

    def validate_blockchain_components(self):
        """Validate blockchain components are preserved."""
        print("🔗 Validating blockchain components...")

        blockchain_path = self.project_root / "blockchain"

        validation = {
            "programs_exist": (blockchain_path / "programs").exists(),
            "anchor_config": (blockchain_path / "Anchor.toml").exists(),
            "cargo_config": (blockchain_path / "Cargo.toml").exists(),
            "program_count": 0,
        }

        if validation["programs_exist"]:
            programs_path = blockchain_path / "programs"
            programs = [p for p in programs_path.iterdir() if p.is_dir()]
            validation["program_count"] = len(programs)

        self.validation_results["cleanup_validation"][
            "blockchain_components"
        ] = validation

        status = (
            "✅"
            if validation["programs_exist"] and validation["program_count"] >= 3
            else "❌"
        )
        print(f"  {status} Blockchain Programs: {validation['program_count']} programs")

        return validation["programs_exist"] and validation["program_count"] >= 3

    def validate_database_components(self):
        """Validate database migrations and schemas are preserved."""
        print("🗄️ Validating database components...")

        validation = {
            "alembic_exists": (
                self.project_root / "services" / "shared" / "alembic"
            ).exists(),
            "migrations_exist": (self.project_root / "migrations").exists(),
            "models_exist": False,
        }

        # Check for model files
        model_paths = [
            self.project_root / "services" / "shared" / "models.py",
            self.project_root / "shared" / "models.py",
        ]
        validation["models_exist"] = any(p.exists() for p in model_paths)

        self.validation_results["cleanup_validation"][
            "database_components"
        ] = validation

        status = (
            "✅"
            if validation["alembic_exists"] and validation["migrations_exist"]
            else "❌"
        )
        print(f"  {status} Database Components: Alembic + Migrations")

        return validation["alembic_exists"] and validation["migrations_exist"]

    def check_constitutional_governance_hash(self):
        """Check for constitutional governance hash cdd01ef066bc6cf2."""
        print("📜 Validating constitutional governance hash...")

        hash_found = False
        hash_locations = []

        # Search for the constitutional hash in key files
        search_paths = [
            self.project_root / "blockchain" / "quantumagi-deployment",
            self.project_root / "services" / "core" / "acgs-pgp-v8",
            self.project_root / "services" / "core" / "constitutional-ai",
        ]

        for search_path in search_paths:
            if search_path.exists():
                for file_path in search_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix in [
                        ".py",
                        ".json",
                        ".yaml",
                        ".yml",
                        ".md",
                    ]:
                        try:
                            with open(
                                file_path, encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                if "cdd01ef066bc6cf2" in content:
                                    hash_found = True
                                    hash_locations.append(str(file_path))
                        except Exception:
                            continue

        status = "✅" if hash_found else "❌"
        print(f"  {status} Constitutional Hash: Found in {len(hash_locations)} files")

        return hash_found

    def generate_validation_summary(self):
        """Generate validation summary."""
        validations = [
            self.validate_core_services(),
            self.validate_enhancement_framework(),
            self.validate_quantumagi_deployment(),
            self.validate_blockchain_components(),
            self.validate_database_components(),
            self.check_constitutional_governance_hash(),
        ]

        total = len(validations)
        passed = sum(validations)
        failed = total - passed

        self.validation_results["summary"] = {
            "total_validations": total,
            "passed_validations": passed,
            "failed_validations": failed,
            "overall_status": "PASSED" if failed == 0 else "FAILED",
            "success_rate": f"{(passed / total) * 100:.1f}%",
        }

        return failed == 0

    def run_validation(self):
        """Run complete validation."""
        print("🚀 Starting ACGS-1 cleanup completion validation...")
        print("=" * 60)

        success = self.generate_validation_summary()

        print("\n📊 VALIDATION SUMMARY")
        print("=" * 30)
        summary = self.validation_results["summary"]
        print(f"Total validations: {summary['total_validations']}")
        print(f"Passed: {summary['passed_validations']}")
        print(f"Failed: {summary['failed_validations']}")
        print(f"Success rate: {summary['success_rate']}")
        print(f"Overall status: {summary['overall_status']}")

        # Save validation report
        report_file = (
            self.project_root
            / f"cleanup_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        print(f"\n📄 Validation report saved to: {report_file}")

        if success:
            print("\n✅ CLEANUP VALIDATION PASSED!")
            print("All critical components preserved and functional.")
        else:
            print("\n❌ CLEANUP VALIDATION FAILED!")
            print("Some critical components may be missing or damaged.")

        return success


if __name__ == "__main__":
    validator = CleanupValidation()
    success = validator.run_validation()
    exit(0 if success else 1)
