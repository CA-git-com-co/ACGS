#!/usr/bin/env python3
"""
Focused ACGS-1 Codebase Reorganization Script
Addresses key reorganization issues without extensive backups
"""

import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FocusedReorganizer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)

    def remove_src_backend_duplicates(self):
        """Remove duplicate services in src/backend that already exist in services/"""
        logger.info("Removing src/backend duplicates...")

        # Services that already exist in services/ and should be removed from src/backend
        duplicates_to_remove = [
            "src/backend/ac_service",
            "src/backend/gs_service",
            "src/backend/pgc_service",
            "src/backend/fv_service",
            "src/backend/auth_service",
            "src/backend/integrity_service",
        ]

        for duplicate in duplicates_to_remove:
            duplicate_path = self.project_root / duplicate
            if duplicate_path.exists():
                logger.info(f"Removing duplicate: {duplicate}")
                shutil.rmtree(duplicate_path)
            else:
                logger.info(f"Already removed: {duplicate}")

    def move_ec_service(self):
        """Move EC service from src/backend to services/core"""
        logger.info("Moving EC service...")

        src_ec = self.project_root / "src/backend/ec_service"
        dst_ec = self.project_root / "services/core/evolutionary-computation"

        if src_ec.exists():
            dst_ec.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Moving EC service: {src_ec} -> {dst_ec}")
            shutil.move(str(src_ec), str(dst_ec))
        else:
            logger.info("EC service already moved or doesn't exist")

    def consolidate_shared_libraries(self):
        """Ensure only one shared library location"""
        logger.info("Consolidating shared libraries...")

        src_shared = self.project_root / "src/backend/shared"
        services_shared = self.project_root / "services/shared"

        if src_shared.exists() and services_shared.exists():
            # Compare and merge if needed, then remove src/backend/shared
            logger.info("Both shared directories exist, removing src/backend/shared")
            shutil.rmtree(src_shared)
        elif src_shared.exists() and not services_shared.exists():
            # Move src/backend/shared to services/shared
            logger.info("Moving shared libraries to services/shared")
            services_shared.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_shared), str(services_shared))

    def consolidate_quantumagi(self):
        """Move quantumagi_core deployment artifacts to blockchain/"""
        logger.info("Consolidating Quantumagi...")

        quantumagi_src = self.project_root / "quantumagi_core"
        blockchain_dir = self.project_root / "blockchain"

        if quantumagi_src.exists():
            # Create deployment directory in blockchain
            deployment_dir = blockchain_dir / "quantumagi-deployment"
            deployment_dir.mkdir(exist_ok=True)

            # Move key deployment files
            deployment_files = [
                "complete_deployment.sh",
                "deploy_quantumagi_devnet.sh",
                "verify_deployment_status.sh",
                "constitution_data.json",
                "governance_accounts.json",
                "initial_policies.json",
            ]

            for file_name in deployment_files:
                src_file = quantumagi_src / file_name
                if src_file.exists():
                    dst_file = deployment_dir / file_name
                    shutil.copy2(src_file, dst_file)
                    logger.info(f"Copied {file_name} to deployment directory")

            # Move docs directory
            docs_src = quantumagi_src / "docs"
            if docs_src.exists():
                docs_dst = deployment_dir / "docs"
                shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
                logger.info("Copied docs to deployment directory")

            # Move log and report files
            for log_file in quantumagi_src.glob("*.log"):
                shutil.copy2(log_file, deployment_dir / log_file.name)
            for json_file in quantumagi_src.glob("*report*.json"):
                shutil.copy2(json_file, deployment_dir / json_file.name)

            logger.info(f"Quantumagi deployment artifacts moved to {deployment_dir}")

    def update_docker_compose_paths(self):
        """Update Docker Compose files with corrected paths"""
        logger.info("Updating Docker Compose files...")

        compose_files = [
            "infrastructure/docker/docker-compose.yml",
            "docker-compose.fixed.yml",
        ]

        path_mappings = {
            "../../src/backend/shared": "../../services/shared",
            "./src/backend/ec_service": "./services/core/evolutionary-computation",
            "src/backend/shared": "services/shared",
        }

        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                with open(file_path, "r") as f:
                    content = f.read()

                original_content = content
                for old_path, new_path in path_mappings.items():
                    content = content.replace(old_path, new_path)

                if content != original_content:
                    with open(file_path, "w") as f:
                        f.write(content)
                    logger.info(f"Updated {compose_file}")

    def update_dockerfile_paths(self):
        """Update Dockerfile paths to use services/shared"""
        logger.info("Updating Dockerfile paths...")

        # Update services/shared/Dockerfile.alembic
        alembic_dockerfile = self.project_root / "services/shared/Dockerfile.alembic"
        if alembic_dockerfile.exists():
            with open(alembic_dockerfile, "r") as f:
                content = f.read()

            # Update paths to use services/shared instead of src/backend/shared
            content = content.replace("src/backend/shared", "services/shared")
            content = content.replace("COPY src/backend/shared", "COPY services/shared")

            with open(alembic_dockerfile, "w") as f:
                f.write(content)
            logger.info("Updated services/shared/Dockerfile.alembic")

    def update_critical_imports(self):
        """Update critical import statements in key files"""
        logger.info("Updating critical import statements...")

        # Key files that need import updates
        critical_files = [
            "services/research/federated-evaluation/federated_service/app/core/cross_platform_adapters.py",
            "services/core/governance-synthesis/gs_service/app/main.py",
        ]

        import_mappings = {
            "from shared.": "from services.shared.",
            "import shared.": "import services.shared.",
            "shared.metrics": "services.shared.metrics",
        }

        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content
                    for old_import, new_import in import_mappings.items():
                        content = content.replace(old_import, new_import)

                    if content != original_content:
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        logger.info(f"Updated imports in {file_path}")

                except Exception as e:
                    logger.warning(f"Failed to update {file_path}: {e}")

    def validate_structure(self):
        """Validate the reorganized structure"""
        logger.info("Validating reorganized structure...")

        # Check key directories exist
        required_dirs = [
            "blockchain/programs/quantumagi-core",
            "services/core/constitutional-ai",
            "services/core/governance-synthesis",
            "services/core/policy-governance",
            "services/core/formal-verification",
            "services/platform/authentication",
            "services/platform/integrity",
            "services/shared",
            "applications/governance-dashboard",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
            else:
                logger.info(f"✅ {dir_path}")

        # Check duplicates are removed
        should_not_exist = [
            "src/backend/ac_service",
            "src/backend/gs_service",
            "src/backend/pgc_service",
            "src/backend/fv_service",
            "src/backend/shared",
        ]

        remaining_duplicates = []
        for dir_path in should_not_exist:
            full_path = self.project_root / dir_path
            if full_path.exists():
                remaining_duplicates.append(dir_path)
            else:
                logger.info(f"✅ Removed: {dir_path}")

        if missing_dirs:
            logger.error(f"Missing required directories: {missing_dirs}")
        if remaining_duplicates:
            logger.warning(f"Remaining duplicates: {remaining_duplicates}")

        success = len(missing_dirs) == 0 and len(remaining_duplicates) == 0
        return success

    def run_focused_reorganization(self):
        """Execute focused reorganization"""
        logger.info("Starting focused ACGS-1 reorganization...")

        try:
            # Phase 1: Remove duplicates
            self.remove_src_backend_duplicates()
            self.move_ec_service()
            self.consolidate_shared_libraries()

            # Phase 2: Consolidate Quantumagi
            self.consolidate_quantumagi()

            # Phase 3: Update configurations
            self.update_docker_compose_paths()
            self.update_dockerfile_paths()
            self.update_critical_imports()

            # Phase 4: Validate
            success = self.validate_structure()

            if success:
                logger.info("✅ Focused reorganization completed successfully!")
            else:
                logger.warning("⚠️ Reorganization completed with some issues")

            return success

        except Exception as e:
            logger.error(f"Reorganization failed: {e}")
            return False


if __name__ == "__main__":
    reorganizer = FocusedReorganizer()
    success = reorganizer.run_focused_reorganization()
    exit(0 if success else 1)
