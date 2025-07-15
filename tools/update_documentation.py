#!/usr/bin/env python3
"""
ACGS-1 Documentation Structure Updates
Updates all documentation to reflect new blockchain-focused directory structure
"""

import logging
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentationUpdater:
    def __init__(self, project_root: str = "/mnt/persist/workspace"):
        self.project_root = Path(project_root)

        # Path mappings for documentation updates
        self.path_mappings = {
            "src/backend/": "services/",
            "src/frontend/": "applications/legacy-frontend/",
            "quantumagi_core/": "blockchain/",
            "src/alphaevolve_gs_engine/": "integrations/alphaevolve-engine/",
            # Service-specific mappings
            "src/backend/ac_service": "services/core/constitutional-ai",
            "src/backend/gs_service": "services/core/governance-synthesis",
            "src/backend/pgc_service": "services/core/policy-governance",
            "src/backend/fv_service": "services/core/formal-verification",
            "src/backend/auth_service": "services/platform/authentication",
            "src/backend/integrity_service": "services/platform/integrity",
            "src/backend/shared": "services/shared",
        }

    def update_main_readme(self):
        """Update main README.md with new structure"""
        logger.info("Updating main README.md...")

        readme_file = self.project_root / "README.md"
        if not readme_file.exists():
            logger.warning("Main README.md not found")
            return False

        with open(readme_file) as f:
            content = f.read()

        # Update path references
        for old_path, new_path in self.path_mappings.items():
            content = content.replace(old_path, new_path)

        # Update service port mappings
        service_ports = """
### Core Services (Ports 8000-8006)

| Service | Port | Location | Purpose |
|---------|------|----------|---------|
| **Authentication** | 8000 | `services/platform/authentication/` | User auth & access control |
| **Constitutional AI** | 8001 | `services/core/constitutional-ai/` | Constitutional principles & compliance |
| **Governance Synthesis** | 8002 | `services/core/governance-synthesis/` | Policy synthesis & management |
| **Policy Governance** | 8003 | `services/core/policy-governance/` | Real-time policy enforcement |
| **Formal Verification** | 8004 | `services/core/formal-verification/` | Mathematical policy validation |
| **Integrity** | 8005 | `services/platform/integrity/` | Data integrity & audit trails |
| **Evolutionary Computation** | 8006 | `services/core/evolutionary-computation/` | WINA optimization & oversight |
"""

        # Insert service ports section if it doesn't exist
        if "### Core Services" not in content:
            # Find a good place to insert it (after main description)
            insertion_point = content.find("## 🏛️ Architecture Overview")
            if insertion_point != -1:
                content = (
                    content[:insertion_point]
                    + service_ports
                    + "\n"
                    + content[insertion_point:]
                )

        with open(readme_file, "w") as f:
            f.write(content)

        logger.info("✅ Updated main README.md")
        return True

    def update_service_readmes(self):
        """Update README files in service directories"""
        logger.info("Updating service README files...")

        service_dirs = [
            "services/core/constitutional-ai",
            "services/core/governance-synthesis",
            "services/core/policy-governance",
            "services/core/formal-verification",
            "services/platform/authentication",
            "services/platform/integrity",
            "services/shared",
        ]

        updated_count = 0
        for service_dir in service_dirs:
            service_path = self.project_root / service_dir
            readme_files = list(service_path.glob("**/README.md"))

            for readme_file in readme_files:
                try:
                    with open(readme_file) as f:
                        content = f.read()

                    # Update path references
                    for old_path, new_path in self.path_mappings.items():
                        content = content.replace(old_path, new_path)

                    # Update relative paths to shared services
                    content = content.replace("../shared", "../../shared")
                    content = content.replace("../../shared/shared", "../../shared")

                    with open(readme_file, "w") as f:
                        f.write(content)

                    updated_count += 1
                    logger.info(
                        f"✅ Updated {readme_file.relative_to(self.project_root)}"
                    )

                except Exception as e:
                    logger.warning(f"Failed to update {readme_file}: {e}")

        logger.info(f"✅ Updated {updated_count} service README files")
        return updated_count > 0

    def update_api_documentation(self):
        """Update API documentation"""
        logger.info("Updating API documentation...")

        api_docs_dir = self.project_root / "docs/api"
        if not api_docs_dir.exists():
            logger.warning("API docs directory not found")
            return False

        api_files = list(api_docs_dir.glob("**/*.md"))
        updated_count = 0

        for api_file in api_files:
            try:
                with open(api_file) as f:
                    content = f.read()

                # Update service endpoint references
                endpoint_mappings = {
                    "localhost:8001": "localhost:8001  # Constitutional AI Service",
                    "localhost:8002": "localhost:8002  # Governance Synthesis Service",
                    "localhost:8003": "localhost:8003  # Policy Governance Service",
                    "localhost:8004": "localhost:8004  # Formal Verification Service",
                    "localhost:8005": "localhost:8005  # Integrity Service",
                    "localhost:8006": "localhost:8006  # Evolutionary Computation Service",
                }

                for old_endpoint, new_endpoint in endpoint_mappings.items():
                    if old_endpoint in content and "# " not in content:
                        content = content.replace(old_endpoint, new_endpoint)

                # Update path references
                for old_path, new_path in self.path_mappings.items():
                    content = content.replace(old_path, new_path)

                with open(api_file, "w") as f:
                    f.write(content)

                updated_count += 1
                logger.info(f"✅ Updated {api_file.relative_to(self.project_root)}")

            except Exception as e:
                logger.warning(f"Failed to update {api_file}: {e}")

        logger.info(f"✅ Updated {updated_count} API documentation files")
        return updated_count > 0

    def update_deployment_guides(self):
        """Update deployment documentation"""
        logger.info("Updating deployment guides...")

        deployment_docs_dir = self.project_root / "docs/deployment"
        if not deployment_docs_dir.exists():
            logger.warning("Deployment docs directory not found")
            return False

        deployment_files = list(deployment_docs_dir.glob("**/*.md"))
        updated_count = 0

        for deploy_file in deployment_files:
            try:
                with open(deploy_file) as f:
                    content = f.read()

                # Update Docker Compose references
                content = content.replace(
                    "docker-compose -f docker-compose.yml",
                    "docker-compose -f infrastructure/docker/docker-compose.yml",
                )

                # Update service build contexts
                content = content.replace("./src/backend/", "./services/")

                # Update Quantumagi deployment references
                content = content.replace(
                    "quantumagi_core/deploy", "blockchain/quantumagi-deployment/deploy"
                )

                # Update path references
                for old_path, new_path in self.path_mappings.items():
                    content = content.replace(old_path, new_path)

                with open(deploy_file, "w") as f:
                    f.write(content)

                updated_count += 1
                logger.info(f"✅ Updated {deploy_file.relative_to(self.project_root)}")

            except Exception as e:
                logger.warning(f"Failed to update {deploy_file}: {e}")

        logger.info(f"✅ Updated {updated_count} deployment guide files")
        return updated_count > 0

    def update_developer_guides(self):
        """Update developer setup and workflow documentation"""
        logger.info("Updating developer guides...")

        dev_docs_dir = self.project_root / "docs/development"
        if not dev_docs_dir.exists():
            logger.warning("Development docs directory not found")
            return False

        dev_files = list(dev_docs_dir.glob("**/*.md"))
        updated_count = 0

        for dev_file in dev_files:
            try:
                with open(dev_file) as f:
                    content = f.read()

                # Update development workflow instructions
                workflow_updates = {
                    "cd src/backend/": "cd services/core/ # or services/platform/",
                    "python -m src.backend": "python -m services",
                    "from services.core.backend": "from services",
                    "import src.backend": "import services",
                }

                for old_workflow, new_workflow in workflow_updates.items():
                    content = content.replace(old_workflow, new_workflow)

                # Update path references
                for old_path, new_path in self.path_mappings.items():
                    content = content.replace(old_path, new_path)

                with open(dev_file, "w") as f:
                    f.write(content)

                updated_count += 1
                logger.info(f"✅ Updated {dev_file.relative_to(self.project_root)}")

            except Exception as e:
                logger.warning(f"Failed to update {dev_file}: {e}")

        logger.info(f"✅ Updated {updated_count} developer guide files")
        return updated_count > 0

    def create_architecture_overview(self):
        """Create updated architecture overview documentation"""
        logger.info("Creating architecture overview...")

        architecture_content = """# ACGS-1 Architecture Overview

## Blockchain-Focused Directory Structure

The ACGS-1 system follows a blockchain-first architecture with clear separation of concerns:

```
ACGS-1/
├── blockchain/                          # 🔗 Solana/Anchor Programs
│   ├── programs/                        # On-chain smart contracts
│   │   ├── quantumagi-core/            # Main governance program
│   │   ├── appeals/                    # Appeals handling program
│   │   └── logging/                    # Event logging program
│   ├── client/                         # Blockchain client libraries
│   ├── tests/                          # Anchor program tests
│   ├── scripts/                        # Deployment & management scripts
│   └── quantumagi-deployment/          # Deployment artifacts & configs
│
├── services/                           # 🏗️ Backend Microservices
│   ├── core/                           # Core governance services
│   │   ├── constitutional-ai/          # Constitutional principles & compliance
│   │   ├── governance-synthesis/       # Policy synthesis & management
│   │   ├── policy-governance/          # Real-time policy enforcement (PGC)
│   │   └── formal-verification/        # Mathematical policy validation
│   ├── platform/                       # Platform infrastructure services
│   │   ├── authentication/             # User authentication & authorization
│   │   ├── integrity/                  # Data integrity & audit trails
│   │   └── workflow/                   # Process orchestration
│   ├── research/                       # Research & experimentation services
│   │   ├── federated-evaluation/       # Federated learning evaluation
│   │   └── research-platform/          # Research infrastructure
│   └── shared/                         # Shared libraries & utilities
│
├── applications/                       # 🖥️ Frontend Applications
│   ├── governance-dashboard/           # Main governance interface
│   ├── constitutional-council/         # Council management interface
│   ├── public-consultation/            # Public participation portal
│   └── admin-panel/                    # Administrative interface
│
├── integrations/                       # 🔗 Integration Layer
│   ├── quantumagi-bridge/             # Blockchain-backend bridge
│   └── alphaevolve-engine/            # AlphaEvolve AI integration
│
├── infrastructure/                     # 🏗️ Infrastructure & Operations
│   ├── docker/                        # Container configurations
│   ├── kubernetes/                    # Orchestration manifests
│   └── monitoring/                    # Observability setup
│
├── tools/                             # 🛠️ Development Tools
├── tests/                             # 🧪 Comprehensive Test Suites
├── docs/                              # 📚 Documentation
└── scripts/                           # 📜 Automation Scripts
```

## Service Communication Architecture

### Core Service Mesh (Ports 8000-8006)

```mermaid
graph TB
    A[Authentication:8000] --> B[Constitutional AI:8001]
    B --> C[Governance Synthesis:8002]
    C --> D[Policy Governance:8003]
    D --> E[Formal Verification:8004]
    E --> F[Integrity:8005]
    F --> G[Evolutionary Computation:8006]

    H[Blockchain Programs] --> D
    I[Frontend Applications] --> A
    J[External Integrations] --> C
```

### Data Flow Architecture

1. **Authentication Layer**: All requests authenticated via port 8000
2. **Constitutional AI**: Manages principles and compliance (port 8001)
3. **Governance Synthesis**: Generates policies from principles (port 8002)
4. **Policy Governance**: Real-time enforcement via PGC (port 8003)
5. **Formal Verification**: Mathematical validation (port 8004)
6. **Integrity Service**: Audit trails and data consistency (port 8005)
7. **Evolutionary Computation**: WINA optimization and oversight (port 8006)

## Blockchain Integration

### Quantumagi Programs on Solana Devnet

- **Quantumagi Core**: `8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4`  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
- **Appeals Program**: `CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ`  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
- **Logging Program**: Ready for deployment

### Constitutional Governance Workflow

1. **Policy Creation**: Draft → Review → Voting → Implementation
2. **Constitutional Compliance**: Real-time validation against principles
3. **Policy Enforcement**: On-chain enforcement via PGC
4. **WINA Oversight**: Continuous monitoring and optimization
5. **Audit & Transparency**: Complete audit trails and public transparency

## Performance Targets

- **Response Times**: <2s for 95% of requests
- **Availability**: >99.5% uptime
- **Governance Costs**: <0.01 SOL per governance action
- **Test Coverage**: >80% for Anchor programs
- **Concurrent Users**: >1000 simultaneous governance actions

## Development Workflow

1. **Blockchain Development**: Use `blockchain/` directory with Anchor framework
2. **Service Development**: Use `services/core/` or `services/platform/`
3. **Frontend Development**: Use `applications/` directory
4. **Integration Development**: Use `integrations/` directory
5. **Testing**: Use `tests/` with unit, integration, and e2e suites
6. **Deployment**: Use `infrastructure/docker/` for containerization

This architecture ensures scalability, maintainability, and clear separation of blockchain and off-chain components while maintaining constitutional governance principles.
"""

        arch_file = self.project_root / "docs/architecture/REORGANIZED_ARCHITECTURE.md"
        arch_file.parent.mkdir(parents=True, exist_ok=True)

        with open(arch_file, "w") as f:
            f.write(architecture_content)

        logger.info("✅ Created architecture overview documentation")
        return True

    def run_documentation_updates(self):
        """Execute all documentation updates"""
        logger.info("Starting documentation structure updates...")

        try:
            results = {
                "main_readme": self.update_main_readme(),
                "service_readmes": self.update_service_readmes(),
                "api_documentation": self.update_api_documentation(),
                "deployment_guides": self.update_deployment_guides(),
                "developer_guides": self.update_developer_guides(),
                "architecture_overview": self.create_architecture_overview(),
            }

            success_count = sum(1 for result in results.values() if result)
            total_count = len(results)

            if success_count == total_count:
                logger.info("✅ All documentation updates completed successfully!")
            else:
                logger.warning(
                    f"⚠️ {success_count}/{total_count} documentation updates completed"
                )

            return success_count == total_count

        except Exception as e:
            logger.error(f"Documentation update failed: {e}")
            return False


if __name__ == "__main__":
    updater = DocumentationUpdater()
    success = updater.run_documentation_updates()
    exit(0 if success else 1)
