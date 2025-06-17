#!/usr/bin/env python3
"""
Complete ACGS-1 Codebase Reorganization Script
Handles remaining components and finalizes the reorganization
"""

import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompleteReorganizer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)

    def move_alphaevolve_engine(self):
        """Move alphaevolve_gs_engine to integrations"""
        logger.info("Moving AlphaEvolve engine to integrations...")

        src_alphaevolve = self.project_root / "src/alphaevolve_gs_engine"
        dst_alphaevolve = self.project_root / "integrations/alphaevolve-engine"

        if src_alphaevolve.exists():
            # Check if destination already exists
            if dst_alphaevolve.exists():
                logger.info(
                    "AlphaEvolve engine already exists in integrations, merging..."
                )
                # Move contents to existing directory
                for item in src_alphaevolve.iterdir():
                    if item.name not in [".git", "__pycache__"]:
                        dst_item = dst_alphaevolve / item.name
                        if dst_item.exists():
                            if item.is_dir():
                                shutil.rmtree(dst_item)
                            else:
                                dst_item.unlink()
                        shutil.move(str(item), str(dst_item))
                # Remove empty source directory
                shutil.rmtree(src_alphaevolve)
            else:
                # Move entire directory
                dst_alphaevolve.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_alphaevolve), str(dst_alphaevolve))

            logger.info("AlphaEvolve engine moved to integrations/alphaevolve-engine")
        else:
            logger.info("AlphaEvolve engine already moved or doesn't exist")

    def move_federated_evaluation(self):
        """Move federated_evaluation to services/research"""
        logger.info("Moving federated evaluation...")

        src_federated = self.project_root / "src/federated_evaluation"
        dst_federated = (
            self.project_root / "services/research/federated-evaluation-core"
        )

        if src_federated.exists():
            dst_federated.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_federated), str(dst_federated))
            logger.info(
                "Federated evaluation moved to services/research/federated-evaluation-core"
            )
        else:
            logger.info("Federated evaluation already moved or doesn't exist")

    def move_frontend_components(self):
        """Move frontend components to applications"""
        logger.info("Moving frontend components...")

        src_frontend = self.project_root / "src/frontend"
        dst_frontend = self.project_root / "applications/legacy-frontend"

        if src_frontend.exists():
            dst_frontend.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_frontend), str(dst_frontend))
            logger.info("Frontend components moved to applications/legacy-frontend")
        else:
            logger.info("Frontend components already moved or doesn't exist")

    def move_dgm_agent(self):
        """Move DGM agent to tools directory"""
        logger.info("Moving DGM agent...")

        src_dgm = self.project_root / "src/dgm-best_swe_agent"
        dst_dgm = self.project_root / "tools/dgm-best-swe-agent"

        if src_dgm.exists():
            dst_dgm.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_dgm), str(dst_dgm))
            logger.info("DGM agent moved to tools/dgm-best-swe-agent")
        else:
            logger.info("DGM agent already moved or doesn't exist")

    def cleanup_empty_src(self):
        """Remove empty src directory if it exists"""
        logger.info("Cleaning up empty src directory...")

        src_dir = self.project_root / "src"
        if src_dir.exists():
            # Check if only README.md and empty backend directory remain
            remaining_items = list(src_dir.iterdir())
            if len(remaining_items) <= 2:  # README.md and possibly empty backend
                backend_dir = src_dir / "backend"
                if backend_dir.exists() and not any(backend_dir.iterdir()):
                    shutil.rmtree(backend_dir)

                # If only README.md remains, move it to docs
                readme_file = src_dir / "README.md"
                if readme_file.exists():
                    docs_dir = self.project_root / "docs/development"
                    docs_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(
                        str(readme_file), str(docs_dir / "legacy-src-readme.md")
                    )

                # Remove empty src directory
                if src_dir.exists() and not any(src_dir.iterdir()):
                    shutil.rmtree(src_dir)
                    logger.info("Removed empty src directory")
        else:
            logger.info("src directory already removed")

    def update_remaining_docker_files(self):
        """Update remaining Docker files with new paths"""
        logger.info("Updating remaining Docker files...")

        # Update any remaining references to src/alphaevolve_gs_engine
        compose_files = [
            "infrastructure/docker/docker-compose.yml",
            "docker-compose.fixed.yml",
        ]

        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read()

                original_content = content

                # Update alphaevolve engine paths
                content = content.replace(
                    "../../src/alphaevolve_gs_engine/src/alphaevolve_gs_engine",
                    "../../integrations/alphaevolve-engine/src/alphaevolve_gs_engine",
                )
                content = content.replace(
                    "/app/alphaevolve_gs_engine",
                    "/app/integrations/alphaevolve_gs_engine",
                )

                if content != original_content:
                    with open(file_path, "w") as f:
                        f.write(content)
                    logger.info(f"Updated {compose_file}")

    def create_workspace_cargo_toml(self):
        """Create a Cargo workspace file for Rust components"""
        logger.info("Creating Cargo workspace configuration...")

        cargo_toml = self.project_root / "Cargo.toml"
        if not cargo_toml.exists():
            workspace_content = """[workspace]
members = [
    "blockchain/programs/quantumagi-core",
    "blockchain/programs/appeals",
    "blockchain/programs/logging",
]

[workspace.dependencies]
anchor-lang = "0.29.0"
anchor-spl = "0.29.0"
solana-program = "~1.18.22"

[profile.release]
overflow-checks = true
lto = "fat"
codegen-units = 1

[profile.release.build-override]
opt-level = 3
incremental = false
codegen-units = 1
"""
            with open(cargo_toml, "w") as f:
                f.write(workspace_content)
            logger.info("Created Cargo workspace configuration")

    def update_package_json_paths(self):
        """Update package.json files with new paths"""
        logger.info("Updating package.json files...")

        # Update blockchain package.json if needed
        blockchain_package = self.project_root / "blockchain/package.json"
        if blockchain_package.exists():
            logger.info("Blockchain package.json already exists and configured")

    def validate_final_structure(self):
        """Validate the final reorganized structure"""
        logger.info("Validating final structure...")

        # Check that all key directories exist
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
            "integrations/alphaevolve-engine",
            "integrations/quantumagi-bridge",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
            else:
                logger.info(f"✅ {dir_path}")

        # Check that old structure is cleaned up
        should_not_exist = [
            "src/backend",
            "src/alphaevolve_gs_engine",
            "src/federated_evaluation",
            "quantumagi_core",  # Should be moved to blockchain/quantumagi-deployment
        ]

        cleaned_up = []
        remaining = []
        for dir_path in should_not_exist:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                cleaned_up.append(dir_path)
            else:
                remaining.append(dir_path)

        for item in cleaned_up:
            logger.info(f"✅ Cleaned up: {item}")

        if missing_dirs:
            logger.error(f"Missing required directories: {missing_dirs}")
        if remaining:
            logger.warning(f"Old structure remaining: {remaining}")

        success = len(missing_dirs) == 0
        return success

    def run_complete_reorganization(self):
        """Execute complete reorganization"""
        logger.info("Starting complete ACGS-1 reorganization...")

        try:
            # Phase 1: Move remaining components
            self.move_alphaevolve_engine()
            self.move_federated_evaluation()
            self.move_frontend_components()
            self.move_dgm_agent()

            # Phase 2: Clean up
            self.cleanup_empty_src()

            # Phase 3: Update configurations
            self.update_remaining_docker_files()
            self.create_workspace_cargo_toml()
            self.update_package_json_paths()

            # Phase 4: Final validation
            success = self.validate_final_structure()

            if success:
                logger.info("✅ Complete reorganization finished successfully!")
                logger.info(
                    "🎯 ACGS-1 now follows blockchain development best practices"
                )
            else:
                logger.warning("⚠️ Reorganization completed with some issues")

            return success

        except Exception as e:
            logger.error(f"Complete reorganization failed: {e}")
            return False


if __name__ == "__main__":
    reorganizer = CompleteReorganizer()
    success = reorganizer.run_complete_reorganization()
    exit(0 if success else 1)
