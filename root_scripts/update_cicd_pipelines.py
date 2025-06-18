#!/usr/bin/env python3
"""
ACGS-1 CI/CD Pipeline Configuration Updates
Updates all GitHub Actions workflows for new blockchain-focused directory structure
"""

import logging
import re
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CICDUpdater:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.workflows_dir = self.project_root / ".github/workflows"

        # Path mappings for updates
        self.path_mappings = {
            # Old paths -> New paths
            "src/backend/ec_service": "services/core/evolutionary-computation/ec_service",
            "src/backend/ac_service": "services/core/constitutional-ai/ac_service",
            "src/backend/gs_service": "services/core/governance-synthesis/gs_service",
            "src/backend/pgc_service": "services/core/policy-governance/pgc_service",
            "src/backend/fv_service": "services/core/formal-verification/fv_service",
            "src/backend/auth_service": "services/platform/authentication/auth_service",
            "src/backend/integrity_service": "services/platform/integrity/integrity_service",
            "src/backend/shared": "services/shared",
            "src/frontend": "applications/legacy-frontend",
            "quantumagi_core": "blockchain",
            "quantumagi_core/**": "blockchain/**",
            # Test paths
            "tests/unit": "tests/unit",
            "tests/integration": "tests/integration",
            "tests/e2e": "tests/e2e",
            # Service matrix updates
            "'ec_service'": "'evolutionary-computation'",
        }

        # Service matrix for Docker builds
        self.new_service_matrix = [
            {
                "name": "constitutional-ai",
                "path": "services/core/constitutional-ai/ac_service",
                "dockerfile": "services/core/constitutional-ai/ac_service/Dockerfile",
            },
            {
                "name": "governance-synthesis",
                "path": "services/core/governance-synthesis/gs_service",
                "dockerfile": "services/core/governance-synthesis/gs_service/Dockerfile",
            },
            {
                "name": "policy-governance",
                "path": "services/core/policy-governance/pgc_service",
                "dockerfile": "services/core/policy-governance/pgc_service/Dockerfile",
            },
            {
                "name": "formal-verification",
                "path": "services/core/formal-verification/fv_service",
                "dockerfile": "services/core/formal-verification/fv_service/Dockerfile",
            },
            {
                "name": "authentication",
                "path": "services/platform/authentication/auth_service",
                "dockerfile": "services/platform/authentication/auth_service/Dockerfile",
            },
            {
                "name": "integrity",
                "path": "services/platform/integrity/integrity_service",
                "dockerfile": "services/platform/integrity/integrity_service/Dockerfile",
            },
        ]

    def update_ci_yml(self):
        """Update main CI/CD workflow"""
        logger.info("Updating ci.yml workflow...")

        ci_file = self.workflows_dir / "ci.yml"
        if not ci_file.exists():
            logger.warning("ci.yml not found")
            return False

        with open(ci_file) as f:
            content = f.read()

        # Update path references
        for old_path, new_path in self.path_mappings.items():
            content = content.replace(old_path, new_path)

        # Update service matrix for Docker builds
        content = re.sub(
            r"service: \['ec_service'\]",
            "service: ['constitutional-ai', 'governance-synthesis', 'policy-governance', 'formal-verification', 'authentication', 'integrity']",
            content,
        )

        # Update Docker build context
        content = re.sub(
            r"context: src/backend/\$\{\{ matrix\.service \}\}",
            "context: services/core/${{ matrix.service }}",
            content,
        )

        # Update Dockerfile path
        content = re.sub(
            r"file: src/backend/\$\{\{ matrix\.service \}\}/Dockerfile",
            "file: services/core/${{ matrix.service }}/Dockerfile",
            content,
        )

        with open(ci_file, "w") as f:
            f.write(content)

        logger.info("✅ Updated ci.yml")
        return True

    def update_image_build_yml(self):
        """Update image build workflow"""
        logger.info("Updating image-build.yml workflow...")

        image_build_file = self.workflows_dir / "image-build.yml"
        if not image_build_file.exists():
            logger.warning("image-build.yml not found")
            return False

        with open(image_build_file) as f:
            content = f.read()

        # Replace the entire matrix section with new service structure
        new_matrix = """    strategy:
      matrix:
        include:
          - name: constitutional-ai
            file: services/core/constitutional-ai/ac_service/Dockerfile
            context: services/core/constitutional-ai/ac_service
          - name: governance-synthesis
            file: services/core/governance-synthesis/gs_service/Dockerfile
            context: services/core/governance-synthesis/gs_service
          - name: policy-governance
            file: services/core/policy-governance/pgc_service/Dockerfile
            context: services/core/policy-governance/pgc_service
          - name: formal-verification
            file: services/core/formal-verification/fv_service/Dockerfile
            context: services/core/formal-verification/fv_service
          - name: authentication
            file: services/platform/authentication/auth_service/Dockerfile
            context: services/platform/authentication/auth_service
          - name: integrity
            file: services/platform/integrity/integrity_service/Dockerfile
            context: services/platform/integrity/integrity_service
          - name: legacy-frontend
            file: applications/legacy-frontend/Dockerfile
            context: applications/legacy-frontend
            exists: false  # Mark as non-existent for now"""

        # Replace the matrix section
        content = re.sub(
            r"    strategy:\s*\n      matrix:\s*\n        include:.*?exists: false.*?# Mark as non-existent for now",
            new_matrix,
            content,
            flags=re.DOTALL,
        )

        with open(image_build_file, "w") as f:
            f.write(content)

        logger.info("✅ Updated image-build.yml")
        return True

    def update_solana_anchor_yml(self):
        """Update Solana Anchor workflow"""
        logger.info("Updating solana-anchor.yml workflow...")

        solana_file = self.workflows_dir / "solana-anchor.yml"
        if not solana_file.exists():
            logger.warning("solana-anchor.yml not found")
            return False

        with open(solana_file) as f:
            content = f.read()

        # Remove quantumagi_core references since it's now consolidated into blockchain/
        content = content.replace("'quantumagi_core/**'", "")
        content = content.replace("- 'quantumagi_core/**'", "")
        content = re.sub(
            r"project: \['blockchain', 'quantumagi_core'\]",
            "project: ['blockchain']",
            content,
        )

        # Update deployment artifact paths
        content = content.replace(
            "blockchain/quantumagi-deployment/", "blockchain/quantumagi-deployment/"
        )

        with open(solana_file, "w") as f:
            f.write(content)

        logger.info("✅ Updated solana-anchor.yml")
        return True

    def update_production_deploy_yml(self):
        """Update production deployment workflow"""
        logger.info("Updating production-deploy.yml workflow...")

        deploy_file = self.workflows_dir / "production-deploy.yml"
        if not deploy_file.exists():
            logger.warning("production-deploy.yml not found")
            return False

        with open(deploy_file) as f:
            content = f.read()

        # Update script paths
        content = content.replace(
            "scripts/comprehensive_health_check.sh",
            "scripts/comprehensive_health_check.sh",
        )

        # Update any service references
        for old_path, new_path in self.path_mappings.items():
            content = content.replace(old_path, new_path)

        with open(deploy_file, "w") as f:
            f.write(content)

        logger.info("✅ Updated production-deploy.yml")
        return True

    def create_enhanced_ci_config(self):
        """Create enhanced CI configuration for new structure"""
        logger.info("Creating enhanced CI configuration...")

        enhanced_config = {
            "version": "2.0",
            "structure": "blockchain-focused",
            "services": {
                "core": [
                    "constitutional-ai",
                    "governance-synthesis",
                    "policy-governance",
                    "formal-verification",
                ],
                "platform": ["authentication", "integrity", "workflow"],
                "research": ["federated-evaluation", "research-platform"],
            },
            "blockchain": {
                "programs": ["quantumagi-core", "appeals", "logging"],
                "deployment_artifacts": "blockchain/quantumagi-deployment/",
            },
            "applications": [
                "governance-dashboard",
                "constitutional-council",
                "public-consultation",
                "admin-panel",
            ],
            "test_paths": {
                "unit": "tests/unit/",
                "integration": "tests/integration/",
                "e2e": "tests/e2e/",
                "performance": "tests/performance/",
            },
            "docker_contexts": {
                "services": "services/",
                "applications": "applications/",
                "blockchain": "blockchain/",
            },
        }

        config_file = self.workflows_dir / "enhanced_ci_config.yml"
        with open(config_file, "w") as f:
            yaml.dump(enhanced_config, f, default_flow_style=False)

        logger.info("✅ Created enhanced CI configuration")
        return True

    def validate_workflow_syntax(self):
        """Validate YAML syntax of all workflow files"""
        logger.info("Validating workflow syntax...")

        workflow_files = list(self.workflows_dir.glob("*.yml"))
        valid_files = []
        invalid_files = []

        for workflow_file in workflow_files:
            try:
                with open(workflow_file) as f:
                    yaml.safe_load(f)
                valid_files.append(workflow_file.name)
            except yaml.YAMLError as e:
                invalid_files.append((workflow_file.name, str(e)))

        logger.info(f"✅ Valid workflows: {valid_files}")
        if invalid_files:
            logger.error(f"❌ Invalid workflows: {invalid_files}")

        return len(invalid_files) == 0

    def run_cicd_updates(self):
        """Execute all CI/CD updates"""
        logger.info("Starting CI/CD pipeline updates...")

        try:
            results = {
                "ci_yml": self.update_ci_yml(),
                "image_build_yml": self.update_image_build_yml(),
                "solana_anchor_yml": self.update_solana_anchor_yml(),
                "production_deploy_yml": self.update_production_deploy_yml(),
                "enhanced_config": self.create_enhanced_ci_config(),
                "syntax_validation": self.validate_workflow_syntax(),
            }

            success_count = sum(results.values())
            total_count = len(results)

            if success_count == total_count:
                logger.info("✅ All CI/CD pipeline updates completed successfully!")
            else:
                logger.warning(
                    f"⚠️ {success_count}/{total_count} CI/CD updates completed"
                )

            return success_count == total_count

        except Exception as e:
            logger.error(f"CI/CD update failed: {e}")
            return False


if __name__ == "__main__":
    updater = CICDUpdater()
    success = updater.run_cicd_updates()
    exit(0 if success else 1)
