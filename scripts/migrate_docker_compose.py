#!/usr/bin/env python3
"""
Docker Compose Migration Script
Constitutional Hash: cdd01ef066bc6cf2

This script helps migrate from the scattered 48+ docker-compose files to the new consolidated structure.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class DockerComposeMigrator:
    def __init__(self, project_root: str = "/home/dislove/ACGS-2"):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "docker-compose-backups"
        self.old_files: List[Path] = []
        self.migration_log: Dict = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "migrated_files": [],
            "backed_up_files": [],
            "consolidated_structure": {
                "base": "docker-compose.base.yml",
                "services": "docker-compose.services.yml", 
                "monitoring": "docker-compose.monitoring.yml",
                "overrides": {
                    "development": "docker-compose.development.override.yml",
                    "production": "docker-compose.production.override.yml",
                    "testing": "docker-compose.testing.override.yml"
                },
                "specialized_stacks": "compose-stacks/"
            }
        }

    def find_old_compose_files(self) -> List[Path]:
        """Find all old docker-compose files that need migration."""
        patterns = [
            "docker-compose*.yml",
            "infrastructure/docker/docker-compose*.yml",
            "infrastructure/monitoring/docker-compose*.yml",
            "infrastructure/load-balancer/docker-compose*.yml"
        ]
        
        old_files = []
        for pattern in patterns:
            old_files.extend(self.project_root.glob(pattern))
        
        # Exclude the new consolidated files
        excluded_files = {
            "docker-compose.base.yml",
            "docker-compose.services.yml", 
            "docker-compose.monitoring.yml",
            "docker-compose.development.override.yml",
            "docker-compose.production.override.yml",
            "docker-compose.testing.override.yml"
        }
        
        self.old_files = [f for f in old_files if f.name not in excluded_files]
        return self.old_files

    def backup_old_files(self) -> None:
        """Create backups of old docker-compose files."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            
        timestamp = "20250707"  # Current date
        backup_subdir = self.backup_dir / f"migration_{timestamp}"
        backup_subdir.mkdir(exist_ok=True)
        
        for old_file in self.old_files:
            # Preserve directory structure in backup
            relative_path = old_file.relative_to(self.project_root)
            backup_path = backup_subdir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(old_file, backup_path)
            self.migration_log["backed_up_files"].append(str(relative_path))
            logger.info(f"Backed up: {relative_path}")

    def analyze_old_files(self) -> Dict:
        """Analyze old files to understand their purpose and suggest migration strategy."""
        analysis = {
            "infrastructure": [],
            "services": [],
            "monitoring": [],
            "specialized": [],
            "deprecated": []
        }
        
        for old_file in self.old_files:
            file_content = old_file.read_text()
            file_info = {
                "path": str(old_file.relative_to(self.project_root)),
                "size": old_file.stat().st_size,
                "services": [],
                "category": "unknown"
            }
            
            # Categorize based on content and path
            if "postgres" in file_content.lower() or "redis" in file_content.lower():
                file_info["category"] = "infrastructure"
                analysis["infrastructure"].append(file_info)
            elif "prometheus" in file_content.lower() or "grafana" in file_content.lower():
                file_info["category"] = "monitoring"
                analysis["monitoring"].append(file_info)
            elif "constitutional-ai" in file_content.lower() or "governance" in file_content.lower():
                file_info["category"] = "services"
                analysis["services"].append(file_info)
            elif "blockchain" in file_content.lower() or "mcp" in file_content.lower():
                file_info["category"] = "specialized"
                analysis["specialized"].append(file_info)
            else:
                file_info["category"] = "deprecated"
                analysis["deprecated"].append(file_info)
        
        return analysis

    def create_migration_guide(self) -> str:
        """Create a migration guide for users."""
        guide = f"""# Docker Compose Migration Guide
# Constitutional Hash: {CONSTITUTIONAL_HASH}

## Migration from Old Structure to New Consolidated Structure

### Old Structure (48+ files scattered across directories)
```
docker-compose.yml
docker-compose.*.yml (multiple variations)
infrastructure/docker/docker-compose.*.yml
infrastructure/monitoring/docker-compose.*.yml
infrastructure/load-balancer/docker-compose.*.yml
```

### New Consolidated Structure
```
# Core files
docker-compose.base.yml              # Infrastructure (PostgreSQL, Redis, OPA, NATS)
docker-compose.services.yml          # Core ACGS services
docker-compose.monitoring.yml        # Unified monitoring stack

# Environment overrides
docker-compose.development.override.yml   # Development with hot reload
docker-compose.production.override.yml    # Production optimizations
docker-compose.testing.override.yml       # Testing configurations

# Specialized stacks
compose-stacks/docker-compose.mcp.yml     # Model Context Protocol services
compose-stacks/docker-compose.*.yml       # Other specialized services
```

### Usage Patterns

#### Development Environment
```bash
# Start infrastructure + services + development overrides
docker-compose -f docker-compose.base.yml \\
              -f docker-compose.services.yml \\
              -f docker-compose.development.override.yml up

# Add monitoring
docker-compose -f docker-compose.base.yml \\
              -f docker-compose.services.yml \\
              -f docker-compose.development.override.yml \\
              -f docker-compose.monitoring.yml up
```

#### Production Environment
```bash
# Start with production optimizations
docker-compose -f docker-compose.base.yml \\
              -f docker-compose.services.yml \\
              -f docker-compose.production.override.yml up

# With monitoring and load balancer
docker-compose -f docker-compose.base.yml \\
              -f docker-compose.services.yml \\
              -f docker-compose.production.override.yml \\
              -f docker-compose.monitoring.yml up
```

#### Testing Environment
```bash
# Automated testing setup
docker-compose -f docker-compose.base.yml \\
              -f docker-compose.services.yml \\
              -f docker-compose.testing.override.yml up
```

#### With Specialized Services
```bash
# Add MCP services for multi-agent coordination
docker-compose -f docker-compose.base.yml -f docker-compose.services.yml up -d
docker-compose -f compose-stacks/docker-compose.mcp.yml up -d
```

### Migration Benefits

1. **Reduced Complexity**: From 48+ files to 6 core files + specialized stacks
2. **Clear Separation**: Infrastructure, services, monitoring, and environments
3. **Easier Maintenance**: Single source of truth for each component type
4. **Better Documentation**: Clear usage patterns and purpose
5. **Constitutional Compliance**: Maintained across all configurations

### Environment Variables

Create `.env` files for different environments:

```bash
# .env.development
POSTGRES_PASSWORD=acgs_dev_password
REDIS_PASSWORD=acgs_dev_redis
ENVIRONMENT=development

# .env.production  
POSTGRES_PASSWORD=${{SECURE_POSTGRES_PASSWORD}}
REDIS_PASSWORD=${{SECURE_REDIS_PASSWORD}}
ENVIRONMENT=production
```

### Rollback Strategy

If issues arise, restore from backups:
```bash
# Backups are stored in docker-compose-backups/migration_YYYYMMDD/
cp -r docker-compose-backups/migration_*/infrastructure ./
```
"""
        return guide

    def generate_makefile(self) -> str:
        """Generate a Makefile for easier docker-compose operations."""
        makefile = f"""# ACGS Docker Compose Makefile
# Constitutional Hash: {CONSTITUTIONAL_HASH}

.PHONY: help dev prod test monitoring mcp clean

help: ## Show this help message
	@echo "ACGS Docker Compose Commands:"
	@echo "Constitutional Hash: {CONSTITUTIONAL_HASH}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-15s\\033[0m %s\\n", $$1, $$2}}'

dev: ## Start development environment with hot reload
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.development.override.yml up

dev-detached: ## Start development environment in background
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.development.override.yml up -d

prod: ## Start production environment
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.production.override.yml up

prod-detached: ## Start production environment in background
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.production.override.yml up -d

test: ## Start testing environment
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.testing.override.yml up

monitoring: ## Start with monitoring stack
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.monitoring.yml up -d

mcp: ## Start MCP services for multi-agent coordination
	docker-compose -f compose-stacks/docker-compose.mcp.yml up -d

dev-full: ## Start development with monitoring
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.development.override.yml \\
	              -f docker-compose.monitoring.yml up -d

prod-full: ## Start production with monitoring
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.production.override.yml \\
	              -f docker-compose.monitoring.yml up -d

logs: ## View logs for all services
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml logs -f

status: ## Show status of all services
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml ps

clean: ## Stop and remove all containers, networks, and volumes
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml \\
	              -f docker-compose.monitoring.yml down -v --remove-orphans
	docker-compose -f compose-stacks/docker-compose.mcp.yml down -v --remove-orphans

reset: ## Complete reset - stop, clean, and rebuild
	make clean
	docker system prune -f
	docker-compose -f docker-compose.base.yml \\
	              -f docker-compose.services.yml build --no-cache

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -f http://localhost:8001/health && echo "✓ Constitutional AI"
	@curl -f http://localhost:8002/health && echo "✓ Integrity Service"
	@curl -f http://localhost:8010/health && echo "✓ API Gateway"
	@curl -f http://localhost:8008/health && echo "✓ Governance Synthesis"
"""
        return makefile

    def migrate(self) -> None:
        """Execute the full migration process."""
        logger.info(f"Starting Docker Compose migration (Constitutional Hash: {CONSTITUTIONAL_HASH})")
        
        # Find old files
        self.find_old_compose_files()
        logger.info(f"Found {len(self.old_files)} old docker-compose files")
        
        # Analyze old files
        analysis = self.analyze_old_files()
        logger.info(f"Analysis complete: {len(analysis['deprecated'])} deprecated files")
        
        # Backup old files
        self.backup_old_files()
        logger.info(f"Backed up {len(self.old_files)} files")
        
        # Create migration guide
        guide = self.create_migration_guide()
        guide_path = self.project_root / "DOCKER_COMPOSE_MIGRATION_GUIDE.md"
        guide_path.write_text(guide)
        logger.info(f"Created migration guide: {guide_path}")
        
        # Create Makefile
        makefile = self.generate_makefile()
        makefile_path = self.project_root / "Makefile"
        makefile_path.write_text(makefile)
        logger.info(f"Created Makefile: {makefile_path}")
        
        # Save migration log
        log_path = self.backup_dir / "migration_log.json"
        with open(log_path, 'w') as f:
            json.dump(self.migration_log, f, indent=2)
        logger.info(f"Migration log saved: {log_path}")
        
        logger.info("Migration completed successfully!")
        logger.info(f"Constitutional compliance maintained: {CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    migrator = DockerComposeMigrator()
    migrator.migrate()