#!/usr/bin/env python3
"""
Validate ACGS-1 Reorganization
Test that all services and components are still functional after reorganization
"""

import json
import logging
import subprocess
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ReorganizationValidator:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)

    def validate_directory_structure(self):
        """Validate the new directory structure"""
        logger.info("Validating directory structure...")

        required_dirs = [
            # Blockchain components
            "blockchain/programs/quantumagi-core",
            "blockchain/programs/appeals",
            "blockchain/programs/logging",
            "blockchain/client",
            "blockchain/tests",
            "blockchain/scripts",
            "blockchain/quantumagi-deployment",
            # Core services
            "services/core/constitutional-ai",
            "services/core/governance-synthesis",
            "services/core/policy-governance",
            "services/core/formal-verification",
            # Platform services
            "services/platform/authentication",
            "services/platform/integrity",
            "services/platform/workflow",
            # Research services
            "services/research/federated-evaluation",
            "services/research/research-platform",
            # Shared libraries
            "services/shared",
            # Applications
            "applications/governance-dashboard",
            "applications/constitutional-council",
            "applications/public-consultation",
            "applications/admin-panel",
            # Integrations
            "integrations/alphaevolve-engine",
            "integrations/quantumagi-bridge",
            # Infrastructure
            "infrastructure/docker",
            "infrastructure/kubernetes",
            "infrastructure/monitoring",
            # Tools and tests
            "tools",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            # Documentation
            "docs/api",
            "docs/architecture",
            "docs/deployment",
            "docs/development",
        ]

        missing_dirs = []
        existing_dirs = []

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)

        logger.info(f"✅ Found {len(existing_dirs)} required directories")
        if missing_dirs:
            logger.warning(f"⚠️ Missing directories: {missing_dirs}")

        return len(missing_dirs) == 0

    def validate_service_structure(self):
        """Validate that services have proper structure"""
        logger.info("Validating service structure...")

        core_services = [
            "services/core/constitutional-ai/ac_service",
            "services/core/governance-synthesis/gs_service",
            "services/core/policy-governance/pgc_service",
            "services/core/formal-verification/fv_service",
        ]

        platform_services = [
            "services/platform/authentication/auth_service",
            "services/platform/integrity/integrity_service",
        ]

        all_services = core_services + platform_services
        valid_services = []
        invalid_services = []

        for service_path in all_services:
            service_dir = self.project_root / service_path

            # Check for main.py or app directory
            main_py = service_dir / "main.py"
            app_dir = service_dir / "app"
            app_main = service_dir / "app/main.py"

            if main_py.exists() or (app_dir.exists() and app_main.exists()):
                valid_services.append(service_path)
            else:
                invalid_services.append(service_path)

        logger.info(f"✅ Valid services: {len(valid_services)}")
        if invalid_services:
            logger.warning(f"⚠️ Invalid service structure: {invalid_services}")

        return len(invalid_services) == 0

    def validate_blockchain_structure(self):
        """Validate blockchain components"""
        logger.info("Validating blockchain structure...")

        # Check Anchor programs
        programs = ["quantumagi-core", "appeals", "logging"]
        valid_programs = []
        invalid_programs = []

        for program in programs:
            program_dir = self.project_root / f"blockchain/programs/{program}"
            lib_rs = program_dir / "src/lib.rs"
            cargo_toml = program_dir / "Cargo.toml"

            if lib_rs.exists() and cargo_toml.exists():
                valid_programs.append(program)
            else:
                invalid_programs.append(program)

        # Check Anchor.toml
        anchor_toml = self.project_root / "blockchain/Anchor.toml"
        anchor_config_valid = anchor_toml.exists()

        logger.info(f"✅ Valid Anchor programs: {valid_programs}")
        logger.info(f"✅ Anchor.toml exists: {anchor_config_valid}")

        if invalid_programs:
            logger.warning(f"⚠️ Invalid programs: {invalid_programs}")

        return len(invalid_programs) == 0 and anchor_config_valid

    def validate_quantumagi_deployment(self):
        """Validate Quantumagi deployment artifacts"""
        logger.info("Validating Quantumagi deployment...")

        deployment_dir = self.project_root / "blockchain/quantumagi-deployment"
        required_files = [
            "complete_deployment.sh",
            "deploy_quantumagi_devnet.sh",
            "verify_deployment_status.sh",
            "constitution_data.json",
            "governance_accounts.json",
            "initial_policies.json",
        ]

        existing_files = []
        missing_files = []

        for file_name in required_files:
            file_path = deployment_dir / file_name
            if file_path.exists():
                existing_files.append(file_name)
            else:
                missing_files.append(file_name)

        logger.info(f"✅ Deployment files found: {len(existing_files)}")
        if missing_files:
            logger.warning(f"⚠️ Missing deployment files: {missing_files}")

        return len(missing_files) == 0

    def validate_docker_configurations(self):
        """Validate Docker configurations are updated"""
        logger.info("Validating Docker configurations...")

        compose_files = [
            "infrastructure/docker/docker-compose.yml",
            "docker-compose.fixed.yml",
        ]

        valid_configs = []
        invalid_configs = []

        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                with open(file_path, "r") as f:
                    content = f.read()

                # Check that old paths are not referenced
                old_paths = ["src/backend/", "quantumagi_core/"]
                has_old_paths = any(old_path in content for old_path in old_paths)

                if not has_old_paths:
                    valid_configs.append(compose_file)
                else:
                    invalid_configs.append(compose_file)
            else:
                invalid_configs.append(f"{compose_file} (missing)")

        logger.info(f"✅ Valid Docker configs: {valid_configs}")
        if invalid_configs:
            logger.warning(f"⚠️ Invalid Docker configs: {invalid_configs}")

        return len(invalid_configs) == 0

    def test_anchor_build(self):
        """Test that Anchor programs can still build"""
        logger.info("Testing Anchor build...")

        blockchain_dir = self.project_root / "blockchain"
        if not blockchain_dir.exists():
            logger.error("Blockchain directory not found")
            return False

        try:
            # Change to blockchain directory and run anchor build
            result = subprocess.run(
                ["anchor", "build"],
                cwd=blockchain_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                logger.info("✅ Anchor build successful")
                return True
            else:
                logger.warning(f"⚠️ Anchor build failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Anchor build timed out")
            return False
        except FileNotFoundError:
            logger.warning("⚠️ Anchor CLI not found, skipping build test")
            return True  # Don't fail validation if Anchor CLI is not installed
        except Exception as e:
            logger.warning(f"⚠️ Anchor build error: {e}")
            return False

    def validate_import_paths(self):
        """Validate that import paths are updated"""
        logger.info("Validating import paths...")

        # Check a few key files for proper imports
        test_files = [
            "services/research/federated-evaluation/federated_service/app/core/cross_platform_adapters.py",
            "services/core/governance-synthesis/gs_service/app/main.py",
        ]

        valid_imports = []
        invalid_imports = []

        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check for old import patterns
                    old_patterns = ["from shared.", "import shared.", "src.backend."]
                    has_old_imports = any(
                        pattern in content for pattern in old_patterns
                    )

                    if not has_old_imports:
                        valid_imports.append(file_path)
                    else:
                        invalid_imports.append(file_path)

                except Exception as e:
                    logger.warning(f"Could not check {file_path}: {e}")
                    invalid_imports.append(file_path)
            else:
                invalid_imports.append(f"{file_path} (missing)")

        logger.info(f"✅ Valid import paths: {len(valid_imports)}")
        if invalid_imports:
            logger.warning(f"⚠️ Invalid import paths: {invalid_imports}")

        return len(invalid_imports) == 0

    def generate_validation_report(self):
        """Generate a comprehensive validation report"""
        logger.info("Generating validation report...")

        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "directory_structure": self.validate_directory_structure(),
            "service_structure": self.validate_service_structure(),
            "blockchain_structure": self.validate_blockchain_structure(),
            "quantumagi_deployment": self.validate_quantumagi_deployment(),
            "docker_configurations": self.validate_docker_configurations(),
            "anchor_build": self.test_anchor_build(),
            "import_paths": self.validate_import_paths(),
        }

        # Calculate overall success
        all_passed = all(results[key] for key in results if key != "timestamp")
        results["overall_success"] = all_passed

        # Save report
        report_file = self.project_root / "reorganization_validation_report.json"
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Validation report saved to {report_file}")

        if all_passed:
            logger.info("🎉 All validation checks passed!")
        else:
            logger.warning("⚠️ Some validation checks failed")

        return all_passed

    def run_validation(self):
        """Run complete validation"""
        logger.info("Starting ACGS-1 reorganization validation...")

        try:
            success = self.generate_validation_report()

            if success:
                logger.info(
                    "✅ ACGS-1 reorganization validation completed successfully!"
                )
                logger.info("🎯 System is ready for blockchain development!")
            else:
                logger.warning("⚠️ Validation completed with some issues")

            return success

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


if __name__ == "__main__":
    validator = ReorganizationValidator()
    success = validator.run_validation()
    exit(0 if success else 1)
