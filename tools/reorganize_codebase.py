#!/usr/bin/env python3
"""
ACGS-1 Codebase Reorganization Script
Reorganizes the codebase to follow blockchain development best practices
"""

import logging
import os
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ACGSReorganizer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_reorganization"

        # Define the target structure
        self.target_structure = {
            "blockchain": ["programs", "client", "tests", "scripts"],
            "services": {
                "core": [
                    "constitutional-ai",
                    "governance-synthesis",
                    "policy-governance",
                    "formal-verification",
                ],
                "platform": ["authentication", "integrity", "workflow"],
                "research": ["federated-evaluation", "research-platform"],
                "shared": [],
            },
            "applications": [
                "governance-dashboard",
                "constitutional-council",
                "public-consultation",
                "admin-panel",
            ],
            "integrations": ["quantumagi-bridge", "alphaevolve-engine"],
            "infrastructure": ["docker", "kubernetes", "monitoring"],
            "tests": ["unit", "integration", "e2e", "performance"],
            "docs": ["api", "architecture", "deployment", "development", "research"],
            "scripts": ["setup", "deployment", "maintenance", "validation"],
        }

        # Service mappings for consolidation
        self.service_mappings = {
            # Remove src/backend duplicates, keep services/ structure
            "src/backend/ac_service": None,  # Remove - already in services/core/constitutional-ai
            "src/backend/gs_service": None,  # Remove - already in services/core/governance-synthesis
            "src/backend/pgc_service": None,  # Remove - already in services/core/policy-governance
            "src/backend/fv_service": None,  # Remove - already in services/core/formal-verification
            "src/backend/auth_service": None,  # Remove - already in services/platform/authentication
            "src/backend/integrity_service": None,  # Remove - already in services/platform/integrity
            "src/backend/ec_service": "services/core/evolutionary-computation",  # Move EC service
            "src/backend/shared": None,  # Remove - already in services/shared
            # Consolidate quantumagi_core into blockchain
            "quantumagi_core": "blockchain/quantumagi-deployment",  # Keep deployment artifacts separate
        }

        # Import path mappings for updates
        self.import_mappings = {
            "src.backend.shared": "services.shared",
            "src.backend.ac_service": "services.core.constitutional_ai.ac_service",
            "src.backend.gs_service": "services.core.governance_synthesis.gs_service",
            "src.backend.pgc_service": "services.core.policy_governance.pgc_service",
            "src.backend.fv_service": "services.core.formal_verification.fv_service",
            "src.backend.auth_service": "services.platform.authentication.auth_service",
            "src.backend.integrity_service": "services.platform.integrity.integrity_service",
            "src.backend.ec_service": "services.core.evolutionary_computation.ec_service",
            "shared.": "services.shared.",
            "backend.shared": "services.shared",
        }

    def create_backup(self):
        """Create backup of current state"""
        logger.info("Creating backup of current state...")
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        # Create backup of key directories
        backup_dirs = [
            "src",
            "quantumagi_core",
            "services",
            "applications",
            "blockchain",
            "integrations",
        ]
        self.backup_dir.mkdir(exist_ok=True)

        for dir_name in backup_dirs:
            src_path = self.project_root / dir_name
            if src_path.exists():
                dst_path = self.backup_dir / dir_name
                try:
                    shutil.copytree(
                        src_path, dst_path, symlinks=True, ignore_dangling_symlinks=True
                    )
                    logger.info(f"Backed up {dir_name}")
                except Exception as e:
                    logger.warning(f"Failed to backup {dir_name}: {e}")
                    # Continue with reorganization even if backup fails

    def remove_duplicates(self):
        """Remove duplicate services and consolidate"""
        logger.info("Removing duplicate services...")

        for old_path, new_path in self.service_mappings.items():
            old_full_path = self.project_root / old_path

            if old_full_path.exists():
                if new_path is None:
                    # Remove duplicate
                    logger.info(f"Removing duplicate: {old_path}")
                    shutil.rmtree(old_full_path)
                else:
                    # Move to new location
                    new_full_path = self.project_root / new_path
                    new_full_path.parent.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Moving {old_path} -> {new_path}")
                    shutil.move(str(old_full_path), str(new_full_path))

    def consolidate_quantumagi(self):
        """Consolidate quantumagi_core into blockchain directory"""
        logger.info("Consolidating Quantumagi into blockchain directory...")

        quantumagi_src = self.project_root / "quantumagi_core"
        blockchain_dir = self.project_root / "blockchain"

        if quantumagi_src.exists():
            # Move deployment artifacts to blockchain/quantumagi-deployment
            deployment_dir = blockchain_dir / "quantumagi-deployment"
            deployment_dir.mkdir(exist_ok=True)

            # Files to keep in deployment directory
            deployment_files = [
                "complete_deployment.sh",
                "deploy_quantumagi_devnet.sh",
                "verify_deployment_status.sh",
                "constitution_data.json",
                "governance_accounts.json",
                "initial_policies.json",
                "*.log",
                "*.json",
                "docs/",
            ]

            for pattern in deployment_files:
                for file_path in quantumagi_src.glob(pattern):
                    if file_path.is_file():
                        shutil.copy2(file_path, deployment_dir / file_path.name)
                    elif file_path.is_dir() and file_path.name == "docs":
                        shutil.copytree(
                            file_path, deployment_dir / "docs", dirs_exist_ok=True
                        )

            # Remove the original quantumagi_core directory
            shutil.rmtree(quantumagi_src)
            logger.info(
                "Quantumagi deployment artifacts moved to blockchain/quantumagi-deployment"
            )

    def update_docker_compose_files(self):
        """Update Docker Compose files with new paths"""
        logger.info("Updating Docker Compose files...")

        compose_files = [
            "docker-compose.yml",
            "docker-compose.fixed.yml",
            "docker-compose.prod.yml",
            "docker-compose.staging.yml",
            "infrastructure/docker/docker-compose.yml",
        ]

        path_mappings = {
            "./src/backend/ac_service": "./services/core/constitutional-ai/ac_service",
            "./src/backend/gs_service": "./services/core/governance-synthesis/gs_service",
            "./src/backend/pgc_service": "./services/core/policy-governance/pgc_service",
            "./src/backend/fv_service": "./services/core/formal-verification/fv_service",
            "./src/backend/auth_service": "./services/platform/authentication/auth_service",
            "./src/backend/integrity_service": "./services/platform/integrity/integrity_service",
            "./src/backend/ec_service": "./services/core/evolutionary-computation/ec_service",
            "./src/backend/shared": "./services/shared",
            "../../src/backend/shared": "../../services/shared",
        }

        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read()

                # Update build contexts and volume mounts
                for old_path, new_path in path_mappings.items():
                    content = content.replace(old_path, new_path)

                with open(file_path, "w") as f:
                    f.write(content)

                logger.info(f"Updated {compose_file}")

    def update_import_statements(self):
        """Update Python import statements across the codebase"""
        logger.info("Updating import statements...")

        # Find all Python files
        python_files = []
        for root, _dirs, files in os.walk(self.project_root):
            # Skip backup and build directories
            if any(
                skip in root
                for skip in ["backup", "target", "node_modules", "__pycache__", ".git"]
            ):
                continue

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Update import statements
                for old_import, new_import in self.import_mappings.items():
                    # Handle different import patterns
                    patterns = [
                        f"from {old_import}",
                        f"import {old_import}",
                        f"from {old_import}.",
                        f"import {old_import}.",
                    ]

                    for pattern in patterns:
                        if pattern in content:
                            new_pattern = pattern.replace(old_import, new_import)
                            content = content.replace(pattern, new_pattern)

                # Write back if changed
                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info(
                        f"Updated imports in {py_file.relative_to(self.project_root)}"
                    )

            except Exception as e:
                logger.warning(f"Failed to update {py_file}: {e}")

    def update_dockerfile_paths(self):
        """Update Dockerfile paths"""
        logger.info("Updating Dockerfile paths...")

        # Find all Dockerfiles
        dockerfiles = []
        for root, _dirs, files in os.walk(self.project_root):
            if any(skip in root for skip in ["backup", "target", "node_modules"]):
                continue
            for file in files:
                if file.startswith("Dockerfile"):
                    dockerfiles.append(Path(root) / file)

        for dockerfile in dockerfiles:
            try:
                with open(dockerfile) as f:
                    content = f.read()

                original_content = content

                # Update COPY and ADD statements
                copy_mappings = {
                    "src/backend/shared": "services/shared",
                    "COPY src/backend/shared": "COPY services/shared",
                    "/app/shared": "/app/services/shared",
                }

                for old_path, new_path in copy_mappings.items():
                    content = content.replace(old_path, new_path)

                if content != original_content:
                    with open(dockerfile, "w") as f:
                        f.write(content)
                    logger.info(f"Updated {dockerfile.relative_to(self.project_root)}")

            except Exception as e:
                logger.warning(f"Failed to update {dockerfile}: {e}")

    def validate_reorganization(self):
        """Validate the reorganization was successful"""
        logger.info("Validating reorganization...")

        # Check that key directories exist
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
            "integrations/quantumagi-bridge",
            "integrations/alphaevolve-engine",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
            else:
                logger.info(f"✅ {dir_path}")

        if missing_dirs:
            logger.error(f"Missing directories: {missing_dirs}")
            return False

        # Check that duplicates were removed
        duplicate_dirs = [
            "src/backend/ac_service",
            "src/backend/gs_service",
            "src/backend/pgc_service",
            "src/backend/fv_service",
            "quantumagi_core",
        ]

        remaining_duplicates = []
        for dir_path in duplicate_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                remaining_duplicates.append(dir_path)

        if remaining_duplicates:
            logger.warning(f"Remaining duplicates: {remaining_duplicates}")

        logger.info("Reorganization validation completed")
        return len(missing_dirs) == 0

    def run_reorganization(self):
        """Execute the complete reorganization process"""
        logger.info("Starting ACGS-1 codebase reorganization...")

        try:
            # Phase 1: Backup and prepare
            self.create_backup()

            # Phase 2: Remove duplicates and consolidate
            self.remove_duplicates()
            self.consolidate_quantumagi()

            # Phase 3: Update configuration files
            self.update_docker_compose_files()
            self.update_import_statements()
            self.update_dockerfile_paths()

            # Phase 4: Validate
            success = self.validate_reorganization()

            if success:
                logger.info("✅ ACGS-1 codebase reorganization completed successfully!")
                logger.info(f"Backup created at: {self.backup_dir}")
                return True
            logger.error("❌ Reorganization validation failed")
            return False

        except Exception as e:
            logger.error(f"Reorganization failed: {e}")
            return False


if __name__ == "__main__":
    reorganizer = ACGSReorganizer()
    success = reorganizer.run_reorganization()
    exit(0 if success else 1)
