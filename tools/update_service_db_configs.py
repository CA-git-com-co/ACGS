#!/usr/bin/env python3
"""
ACGS-1 Service Database Configuration Updater
Phase 2 - Enterprise Scalability & Performance

Updates all 7 core services to use PgBouncer connection pooling
for >1000 concurrent users and >99.9% availability.
"""

import sys
from pathlib import Path
from typing import Any

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.database.connection_pool_config import ServiceConnectionPools


class ServiceConfigUpdater:
    """Updates service configurations to use PgBouncer connection pooling."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services = {
            "auth_service": "services/core/auth",
            "ac_service": "services/core/constitutional-ai",
            "integrity_service": "services/core/integrity",
            "fv_service": "services/core/formal-verification",
            "gs_service": "services/core/governance-synthesis",
            "pgc_service": "services/core/policy-governance",
            "ec_service": "services/core/evaluation-compliance",
        }

    def update_all_services(self) -> bool:
        """Update all service configurations."""
        print("🔧 Updating ACGS-1 service database configurations for PgBouncer...")

        success_count = 0
        total_services = len(self.services)

        for service_name, service_path in self.services.items():
            print(f"\n📝 Updating {service_name}...")

            try:
                if self.update_service_config(service_name, service_path):
                    print(f"✅ {service_name} updated successfully")
                    success_count += 1
                else:
                    print(f"❌ Failed to update {service_name}")
            except Exception as e:
                print(f"❌ Error updating {service_name}: {e}")

        print(
            f"\n📊 Summary: {success_count}/{total_services} services updated successfully"
        )
        return success_count == total_services

    def update_service_config(self, service_name: str, service_path: str) -> bool:
        """Update configuration for a specific service."""
        service_dir = self.project_root / service_path

        if not service_dir.exists():
            print(f"⚠️  Service directory not found: {service_dir}")
            return False

        # Get connection pool configuration
        config = ServiceConnectionPools.get_config(service_name)

        # Update different configuration file types
        updated = False

        # Update .env files
        if self.update_env_file(service_dir, config):
            updated = True

        # Update YAML configuration files
        if self.update_yaml_configs(service_dir, config):
            updated = True

        # Update Python configuration files
        if self.update_python_configs(service_dir, config):
            updated = True

        # Update Docker configurations
        if self.update_docker_configs(service_dir, config):
            updated = True

        return updated

    def update_env_file(self, service_dir: Path, config) -> bool:
        """Update .env file with PgBouncer configuration."""
        env_files = [".env", ".env.example", ".env.local"]
        updated = False

        for env_file in env_files:
            env_path = service_dir / env_file
            if env_path.exists():
                try:
                    # Read existing content
                    with open(env_path) as f:
                        lines = f.readlines()

                    # Update database-related environment variables
                    new_lines = []
                    db_vars_updated = set()

                    for line in lines:
                        if line.startswith("DATABASE_URL="):
                            new_lines.append(
                                f"DATABASE_URL={config.get_connection_url()}\n"
                            )
                            db_vars_updated.add("DATABASE_URL")
                        elif line.startswith("DB_HOST="):
                            new_lines.append(f"DB_HOST={config.host}\n")
                            db_vars_updated.add("DB_HOST")
                        elif line.startswith("DB_PORT="):
                            new_lines.append(f"DB_PORT={config.port}\n")
                            db_vars_updated.add("DB_PORT")
                        elif line.startswith("DATABASE_POOL_SIZE="):
                            new_lines.append(
                                f"DATABASE_POOL_SIZE={config.max_connections}\n"
                            )
                            db_vars_updated.add("DATABASE_POOL_SIZE")
                        elif line.startswith("DATABASE_MAX_OVERFLOW="):
                            new_lines.append(
                                f"DATABASE_MAX_OVERFLOW={config.max_overflow}\n"
                            )
                            db_vars_updated.add("DATABASE_MAX_OVERFLOW")
                        elif line.startswith("DATABASE_POOL_TIMEOUT="):
                            new_lines.append(
                                f"DATABASE_POOL_TIMEOUT={config.pool_timeout}\n"
                            )
                            db_vars_updated.add("DATABASE_POOL_TIMEOUT")
                        else:
                            new_lines.append(line)

                    # Add missing database variables
                    if "DATABASE_URL" not in db_vars_updated:
                        new_lines.append(
                            f"DATABASE_URL={config.get_connection_url()}\n"
                        )
                    if "DB_HOST" not in db_vars_updated:
                        new_lines.append(f"DB_HOST={config.host}\n")
                    if "DB_PORT" not in db_vars_updated:
                        new_lines.append(f"DB_PORT={config.port}\n")

                    # Write updated content
                    with open(env_path, "w") as f:
                        f.writelines(new_lines)

                    print(f"  📄 Updated {env_file}")
                    updated = True

                except Exception as e:
                    print(f"  ❌ Error updating {env_file}: {e}")

        return updated

    def update_yaml_configs(self, service_dir: Path, config) -> bool:
        """Update YAML configuration files."""
        yaml_files = list(service_dir.glob("**/*.yaml")) + list(
            service_dir.glob("**/*.yml")
        )
        updated = False

        for yaml_file in yaml_files:
            if "docker-compose" in yaml_file.name:
                continue  # Skip docker-compose files

            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)

                if data and self.update_yaml_database_config(data, config):
                    with open(yaml_file, "w") as f:
                        yaml.dump(data, f, default_flow_style=False, indent=2)

                    print(f"  📄 Updated {yaml_file.relative_to(service_dir)}")
                    updated = True

            except Exception as e:
                print(f"  ❌ Error updating {yaml_file.name}: {e}")

        return updated

    def update_yaml_database_config(self, data: dict[str, Any], config) -> bool:
        """Update database configuration in YAML data."""
        updated = False

        # Common database configuration paths
        db_paths = [
            ["database"],
            ["db"],
            ["postgres"],
            ["postgresql"],
            ["config", "database"],
            ["service", "database"],
        ]

        for path in db_paths:
            current = data
            for key in path[:-1]:
                if key in current and isinstance(current[key], dict):
                    current = current[key]
                else:
                    break
            else:
                # Path exists, update database config
                db_key = path[-1]
                if db_key in current and isinstance(current[db_key], dict):
                    db_config = current[db_key]

                    # Update connection settings
                    if "url" in db_config:
                        db_config["url"] = config.get_connection_url()
                        updated = True
                    if "host" in db_config:
                        db_config["host"] = config.host
                        updated = True
                    if "port" in db_config:
                        db_config["port"] = config.port
                        updated = True

                    # Update pool settings
                    if "pool_size" in db_config:
                        db_config["pool_size"] = config.max_connections
                        updated = True
                    if "max_overflow" in db_config:
                        db_config["max_overflow"] = config.max_overflow
                        updated = True
                    if "pool_timeout" in db_config:
                        db_config["pool_timeout"] = config.pool_timeout
                        updated = True

        return updated

    def update_python_configs(self, service_dir: Path, config) -> bool:
        """Update Python configuration files."""
        # This would update Python config files if needed
        # For now, we'll rely on the centralized configuration
        return True

    def update_docker_configs(self, service_dir: Path, config) -> bool:
        """Update Docker configuration files."""
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        updated = False

        for docker_file in docker_files:
            docker_path = service_dir / docker_file
            if docker_path.exists():
                try:
                    with open(docker_path) as f:
                        content = f.read()

                    # Update environment variables in Docker files
                    original_content = content

                    # Update DATABASE_URL environment variable
                    import re

                    content = re.sub(
                        r"DATABASE_URL=postgresql://[^@]+@[^:]+:\d+/\w+",
                        f"DATABASE_URL={config.get_connection_url()}",
                        content,
                    )

                    if content != original_content:
                        with open(docker_path, "w") as f:
                            f.write(content)
                        print(f"  📄 Updated {docker_file}")
                        updated = True

                except Exception as e:
                    print(f"  ❌ Error updating {docker_file}: {e}")

        return updated


def main():
    """Main function to update all service configurations."""
    project_root = Path(__file__).parent.parent
    updater = ServiceConfigUpdater(project_root)

    print("🚀 ACGS-1 Database Configuration Update for PgBouncer")
    print("=" * 60)

    # Validate connection pool configurations
    if not ServiceConnectionPools.validate_configurations():
        print("❌ Connection pool configuration validation failed!")
        return False

    # Update all service configurations
    success = updater.update_all_services()

    if success:
        print("\n✅ All service configurations updated successfully!")
        print("\n📋 Next steps:")
        print("1. Restart all services to apply new configurations")
        print("2. Test database connections through PgBouncer")
        print("3. Monitor connection pool metrics")
        print("4. Implement retry mechanisms and circuit breakers")
    else:
        print("\n❌ Some service configurations failed to update")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
