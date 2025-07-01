#!/usr/bin/env python3
"""
DGM Database Migration Runner

Comprehensive migration runner with rollback capabilities and data integrity checks.
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DGMMigrationRunner:
    """Manages DGM database migrations with rollback capabilities."""

    def __init__(self, database_url: str):
        """Initialize migration runner."""
        self.database_url = database_url
        self.engine = None
        self.migration_history: list[dict[str, Any]] = []

    def initialize(self):
        """Initialize database connection."""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            logger.info("Migration runner initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize migration runner: {e}")
            return False

    def check_prerequisites(self) -> dict[str, Any]:
        """Check migration prerequisites."""
        checks = {
            "database_connection": False,
            "alembic_available": False,
            "migration_files_exist": False,
            "schema_permissions": False,
            "errors": [],
        }

        try:
            # Check database connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                checks["database_connection"] = True
                logger.info("✅ Database connection successful")
        except Exception as e:
            checks["errors"].append(f"Database connection failed: {e}")
            logger.error(f"❌ Database connection failed: {e}")

        # Check Alembic availability
        try:
            result = subprocess.run(
                ["alembic", "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                checks["alembic_available"] = True
                logger.info("✅ Alembic is available")
            else:
                checks["errors"].append("Alembic not available or not working")
        except Exception as e:
            checks["errors"].append(f"Alembic check failed: {e}")
            logger.error(f"❌ Alembic check failed: {e}")

        # Check migration files exist
        migration_files = [
            "migrations/versions/001_create_dgm_schema.py",
            "migrations/versions/002_create_dgm_bandit_workspace_config.py",
            "migrations/versions/003_create_dgm_indexes.py",
            "migrations/versions/004_insert_dgm_default_data.py",
        ]

        missing_files = []
        for file_path in migration_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if not missing_files:
            checks["migration_files_exist"] = True
            logger.info("✅ All migration files exist")
        else:
            checks["errors"].append(f"Missing migration files: {missing_files}")
            logger.error(f"❌ Missing migration files: {missing_files}")

        # Check schema creation permissions
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS dgm_test"))
                conn.execute(text("DROP SCHEMA dgm_test"))
                checks["schema_permissions"] = True
                logger.info("✅ Schema creation permissions verified")
        except Exception as e:
            checks["errors"].append(f"Schema permissions check failed: {e}")
            logger.error(f"❌ Schema permissions check failed: {e}")

        return checks

    def create_backup(self, backup_name: str | None = None) -> dict[str, Any]:
        """Create database backup before migration."""
        if not backup_name:
            backup_name = f"dgm_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_result = {
            "backup_name": backup_name,
            "success": False,
            "backup_path": None,
            "tables_backed_up": [],
            "errors": [],
        }

        try:
            with self.engine.connect() as conn:
                # Create backup schema
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS dgm_backups"))
                conn.execute(
                    text(f"CREATE SCHEMA IF NOT EXISTS dgm_backups.{backup_name}")
                )

                # Check if DGM schema exists
                result = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM information_schema.schemata 
                    WHERE schema_name = 'dgm'
                """
                    )
                )

                if result.scalar() > 0:
                    # Backup existing DGM tables
                    tables_query = conn.execute(
                        text(
                            """
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'dgm'
                    """
                        )
                    )

                    for (table_name,) in tables_query:
                        try:
                            conn.execute(
                                text(
                                    f"""
                                CREATE TABLE dgm_backups.{backup_name}.{table_name} AS
                                SELECT * FROM dgm.{table_name}
                            """
                                )
                            )
                            backup_result["tables_backed_up"].append(table_name)
                        except Exception as e:
                            backup_result["errors"].append(
                                f"Error backing up {table_name}: {e}"
                            )

                conn.commit()
                backup_result["success"] = True
                backup_result["backup_path"] = f"dgm_backups.{backup_name}"
                logger.info(f"✅ Backup created: {backup_name}")

        except Exception as e:
            backup_result["errors"].append(f"Backup creation failed: {e}")
            logger.error(f"❌ Backup creation failed: {e}")

        return backup_result

    def run_migrations(self) -> dict[str, Any]:
        """Run DGM migrations using Alembic."""
        migration_result = {
            "success": False,
            "migrations_applied": [],
            "current_revision": None,
            "errors": [],
        }

        try:
            # Set environment variables
            env = os.environ.copy()
            env["DATABASE_URL"] = self.database_url

            # Run Alembic upgrade
            result = subprocess.run(
                ["alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                migration_result["success"] = True
                logger.info("✅ Migrations completed successfully")
                logger.info(f"Migration output: {result.stdout}")

                # Get current revision
                revision_result = subprocess.run(
                    ["alembic", "-c", "migrations/alembic.ini", "current"],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=env,
                )

                if revision_result.returncode == 0:
                    migration_result["current_revision"] = (
                        revision_result.stdout.strip()
                    )

            else:
                migration_result["errors"].append(f"Migration failed: {result.stderr}")
                logger.error(f"❌ Migration failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            migration_result["errors"].append("Migration timed out after 5 minutes")
            logger.error("❌ Migration timed out")
        except Exception as e:
            migration_result["errors"].append(f"Migration execution failed: {e}")
            logger.error(f"❌ Migration execution failed: {e}")

        return migration_result

    def verify_migration(self) -> dict[str, Any]:
        """Verify migration success and data integrity."""
        verification_result = {
            "schema_exists": False,
            "tables_created": [],
            "indexes_created": [],
            "data_integrity": False,
            "constitutional_compliance": False,
            "errors": [],
        }

        try:
            with self.engine.connect() as conn:
                # Check schema existence
                result = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM information_schema.schemata 
                    WHERE schema_name = 'dgm'
                """
                    )
                )
                verification_result["schema_exists"] = result.scalar() > 0

                # Check table existence
                expected_tables = [
                    "dgm_archive",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "metric_aggregations",
                ]

                for table in expected_tables:
                    result = conn.execute(
                        text(
                            f"""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = 'dgm' AND table_name = '{table}'
                    """
                        )
                    )
                    if result.scalar() > 0:
                        verification_result["tables_created"].append(table)

                # Check default data
                config_count = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM dgm.system_configurations
                """
                    )
                ).scalar()

                bandit_count = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM dgm.bandit_states
                """
                    )
                ).scalar()

                verification_result["data_integrity"] = (
                    config_count > 0 and bandit_count > 0
                )

                # Check constitutional compliance setup
                constitutional_hash = conn.execute(
                    text(
                        """
                    SELECT value FROM dgm.system_configurations 
                    WHERE key = 'constitutional_hash'
                """
                    )
                ).scalar()

                verification_result["constitutional_compliance"] = (
                    constitutional_hash == "cdd01ef066bc6cf2"
                )

                logger.info("✅ Migration verification completed")

        except Exception as e:
            verification_result["errors"].append(f"Verification failed: {e}")
            logger.error(f"❌ Verification failed: {e}")

        return verification_result

    def rollback_migration(self, target_revision: str = "base") -> dict[str, Any]:
        """Rollback migration to specified revision."""
        rollback_result = {
            "success": False,
            "target_revision": target_revision,
            "errors": [],
        }

        try:
            env = os.environ.copy()
            env["DATABASE_URL"] = self.database_url

            result = subprocess.run(
                [
                    "alembic",
                    "-c",
                    "migrations/alembic.ini",
                    "downgrade",
                    target_revision,
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,
            )

            if result.returncode == 0:
                rollback_result["success"] = True
                logger.info(f"✅ Rollback to {target_revision} completed successfully")
            else:
                rollback_result["errors"].append(f"Rollback failed: {result.stderr}")
                logger.error(f"❌ Rollback failed: {result.stderr}")

        except Exception as e:
            rollback_result["errors"].append(f"Rollback execution failed: {e}")
            logger.error(f"❌ Rollback execution failed: {e}")

        return rollback_result


def main():
    """Main migration runner function."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)

    runner = DGMMigrationRunner(database_url)

    if not runner.initialize():
        logger.error("❌ Failed to initialize migration runner")
        sys.exit(1)

    # Check prerequisites
    logger.info("🔍 Checking migration prerequisites...")
    prereq_check = runner.check_prerequisites()

    if prereq_check["errors"]:
        logger.error("❌ Prerequisites check failed:")
        for error in prereq_check["errors"]:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Create backup
    logger.info("💾 Creating database backup...")
    backup_result = runner.create_backup()

    if not backup_result["success"]:
        logger.error("❌ Backup creation failed:")
        for error in backup_result["errors"]:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Run migrations
    logger.info("🚀 Running DGM migrations...")
    migration_result = runner.run_migrations()

    if not migration_result["success"]:
        logger.error("❌ Migration failed:")
        for error in migration_result["errors"]:
            logger.error(f"  - {error}")

        # Attempt rollback
        logger.info("🔄 Attempting rollback...")
        rollback_result = runner.rollback_migration()
        if rollback_result["success"]:
            logger.info("✅ Rollback completed successfully")
        else:
            logger.error("❌ Rollback also failed - manual intervention required")

        sys.exit(1)

    # Verify migration
    logger.info("✅ Verifying migration results...")
    verification_result = runner.verify_migration()

    if verification_result["errors"]:
        logger.warning("⚠️ Verification warnings:")
        for error in verification_result["errors"]:
            logger.warning(f"  - {error}")

    logger.info("🎉 DGM database migration completed successfully!")
    logger.info("📊 Migration Summary:")
    logger.info(f"  - Schema created: {verification_result['schema_exists']}")
    logger.info(f"  - Tables created: {len(verification_result['tables_created'])}")
    logger.info(f"  - Data integrity: {verification_result['data_integrity']}")
    logger.info(
        f"  - Constitutional compliance: {verification_result['constitutional_compliance']}"
    )
    logger.info(f"  - Backup location: {backup_result['backup_path']}")


if __name__ == "__main__":
    main()
