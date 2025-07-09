#!/usr/bin/env python3
"""
ACGS-1 Database Migration Framework

Comprehensive database migration system for ACGS-1 Constitutional Governance System.
Supports automated migrations, rollbacks, and schema versioning across all environments.
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import asyncpg
from alembic.config import Config

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationInfo:
    """Information about a database migration."""

    version: str
    description: str
    file_path: str
    checksum: str
    applied_at: datetime | None = None
    rollback_script: str | None = None


class DatabaseMigrator:
    """Main database migration manager."""

    def __init__(self, config_path: str = "alembic.ini"):
        """Initialize the database migrator."""
        self.config_path = config_path
        self.alembic_cfg = Config(config_path)
        self.migrations_dir = Path("migrations")
        self.rollback_dir = Path("migrations/rollbacks")

        # Ensure directories exist
        self.migrations_dir.mkdir(exist_ok=True)
        self.rollback_dir.mkdir(exist_ok=True)

    async def get_database_connection(self) -> asyncpg.Connection:
        """Get database connection from environment variables."""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        return await asyncpg.connect(database_url)

    async def initialize_migration_table(self) -> None:
        """Initialize the migration tracking table."""
        conn = await self.get_database_connection()
        try:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS acgs_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    description TEXT NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    applied_by VARCHAR(255) DEFAULT CURRENT_USER,
                    execution_time_ms INTEGER,
                    rollback_script TEXT
                )
            """
            )

            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_acgs_migrations_applied_at 
                ON acgs_migrations(applied_at)
            """
            )

            logger.info("Migration tracking table initialized")
        finally:
            await conn.close()

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    async def get_applied_migrations(self) -> list[MigrationInfo]:
        """Get list of applied migrations from database."""
        conn = await self.get_database_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT version, description, checksum, applied_at, rollback_script
                FROM acgs_migrations
                ORDER BY applied_at
            """
            )

            return [
                MigrationInfo(
                    version=row["version"],
                    description=row["description"],
                    file_path="",  # Not stored in DB
                    checksum=row["checksum"],
                    applied_at=row["applied_at"],
                    rollback_script=row["rollback_script"],
                )
                for row in rows
            ]
        finally:
            await conn.close()

    def get_pending_migrations(self) -> list[MigrationInfo]:
        """Get list of pending migrations from filesystem."""
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        pending_migrations = []

        for file_path in migration_files:
            if file_path.name.startswith("rollback_"):
                continue

            version = file_path.stem
            checksum = self.calculate_file_checksum(file_path)

            # Read description from file header
            description = self._extract_description(file_path)

            # Check for rollback script
            rollback_file = self.rollback_dir / f"rollback_{file_path.name}"
            rollback_script = None
            if rollback_file.exists():
                with open(rollback_file) as f:
                    rollback_script = f.read()

            pending_migrations.append(
                MigrationInfo(
                    version=version,
                    description=description,
                    file_path=str(file_path),
                    checksum=checksum,
                    rollback_script=rollback_script,
                )
            )

        return pending_migrations

    def _extract_description(self, file_path: Path) -> str:
        """Extract description from migration file header."""
        with open(file_path) as f:
            first_line = f.readline().strip()
            if first_line.startswith("-- Description:"):
                return first_line.replace("-- Description:", "").strip()
            if first_line.startswith("--"):
                return first_line.replace("--", "").strip()
        return f"Migration {file_path.stem}"

    async def apply_migration(self, migration: MigrationInfo) -> bool:
        """Apply a single migration."""
        logger.info(
            f"Applying migration: {migration.version} - {migration.description}"
        )

        conn = await self.get_database_connection()
        start_time = datetime.now()

        try:
            # Start transaction
            async with conn.transaction():
                # Read and execute migration SQL
                with open(migration.file_path) as f:
                    sql_content = f.read()

                # Remove comments and empty lines for execution
                sql_statements = [
                    stmt.strip()
                    for stmt in sql_content.split(";")
                    if stmt.strip() and not stmt.strip().startswith("--")
                ]

                for statement in sql_statements:
                    if statement:
                        await conn.execute(statement)

                # Record migration in tracking table
                execution_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )

                await conn.execute(
                    """
                    INSERT INTO acgs_migrations 
                    (version, description, checksum, execution_time_ms, rollback_script)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                    migration.version,
                    migration.description,
                    migration.checksum,
                    execution_time,
                    migration.rollback_script,
                )

                logger.info(
                    f"Migration {migration.version} applied successfully in {execution_time}ms"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False
        finally:
            await conn.close()

    async def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration."""
        logger.info(f"Rolling back migration: {version}")

        conn = await self.get_database_connection()

        try:
            # Get migration info
            row = await conn.fetchrow(
                """
                SELECT rollback_script FROM acgs_migrations WHERE version = $1
            """,
                version,
            )

            if not row or not row["rollback_script"]:
                logger.error(f"No rollback script found for migration {version}")
                return False

            # Start transaction
            async with conn.transaction():
                # Execute rollback script
                rollback_statements = [
                    stmt.strip()
                    for stmt in row["rollback_script"].split(";")
                    if stmt.strip() and not stmt.strip().startswith("--")
                ]

                for statement in rollback_statements:
                    if statement:
                        await conn.execute(statement)

                # Remove migration record
                await conn.execute(
                    """
                    DELETE FROM acgs_migrations WHERE version = $1
                """,
                    version,
                )

                logger.info(f"Migration {version} rolled back successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False
        finally:
            await conn.close()

    async def validate_migrations(self) -> bool:
        """Validate migration integrity."""
        logger.info("Validating migration integrity...")

        applied_migrations = await self.get_applied_migrations()
        pending_migrations = self.get_pending_migrations()

        # Check for checksum mismatches
        for applied in applied_migrations:
            # Find corresponding file
            file_path = self.migrations_dir / f"{applied.version}.sql"
            if file_path.exists():
                current_checksum = self.calculate_file_checksum(file_path)
                if current_checksum != applied.checksum:
                    logger.error(f"Checksum mismatch for migration {applied.version}")
                    return False

        logger.info("Migration validation completed successfully")
        return True

    async def get_migration_status(self) -> dict[str, Any]:
        """Get comprehensive migration status."""
        applied_migrations = await self.get_applied_migrations()
        pending_migrations = self.get_pending_migrations()

        # Filter out already applied migrations
        applied_versions = {m.version for m in applied_migrations}
        truly_pending = [
            m for m in pending_migrations if m.version not in applied_versions
        ]

        return {
            "applied_count": len(applied_migrations),
            "pending_count": len(truly_pending),
            "applied_migrations": [
                {
                    "version": m.version,
                    "description": m.description,
                    "applied_at": m.applied_at.isoformat() if m.applied_at else None,
                }
                for m in applied_migrations
            ],
            "pending_migrations": [
                {
                    "version": m.version,
                    "description": m.description,
                    "file_path": m.file_path,
                }
                for m in truly_pending
            ],
        }

    async def migrate_up(self, target_version: str | None = None) -> bool:
        """Apply all pending migrations up to target version."""
        logger.info("Starting database migration...")

        await self.initialize_migration_table()

        if not await self.validate_migrations():
            logger.error("Migration validation failed")
            return False

        applied_migrations = await self.get_applied_migrations()
        pending_migrations = self.get_pending_migrations()

        # Filter out already applied migrations
        applied_versions = {m.version for m in applied_migrations}
        to_apply = [m for m in pending_migrations if m.version not in applied_versions]

        # Filter by target version if specified
        if target_version:
            to_apply = [m for m in to_apply if m.version <= target_version]

        if not to_apply:
            logger.info("No pending migrations to apply")
            return True

        logger.info(f"Applying {len(to_apply)} migrations...")

        for migration in to_apply:
            if not await self.apply_migration(migration):
                logger.error(f"Migration failed at {migration.version}")
                return False

        logger.info("All migrations applied successfully")
        return True

    async def migrate_down(self, target_version: str) -> bool:
        """Rollback migrations down to target version."""
        logger.info(f"Rolling back migrations to version {target_version}")

        applied_migrations = await self.get_applied_migrations()

        # Find migrations to rollback (in reverse order)
        to_rollback = [
            m for m in reversed(applied_migrations) if m.version > target_version
        ]

        if not to_rollback:
            logger.info("No migrations to rollback")
            return True

        logger.info(f"Rolling back {len(to_rollback)} migrations...")

        for migration in to_rollback:
            if not await self.rollback_migration(migration.version):
                logger.error(f"Rollback failed at {migration.version}")
                return False

        logger.info("Rollback completed successfully")
        return True


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ACGS-1 Database Migration Tool")
    parser.add_argument(
        "command",
        choices=["status", "migrate", "rollback", "validate"],
        help="Migration command to execute",
    )
    parser.add_argument("--target", help="Target migration version")
    parser.add_argument(
        "--config", default="alembic.ini", help="Alembic configuration file"
    )

    args = parser.parse_args()

    migrator = DatabaseMigrator(args.config)

    try:
        if args.command == "status":
            status = await migrator.get_migration_status()
            print(json.dumps(status, indent=2))

        elif args.command == "migrate":
            success = await migrator.migrate_up(args.target)
            sys.exit(0 if success else 1)

        elif args.command == "rollback":
            if not args.target:
                logger.error("Target version required for rollback")
                sys.exit(1)
            success = await migrator.migrate_down(args.target)
            sys.exit(0 if success else 1)

        elif args.command == "validate":
            success = await migrator.validate_migrations()
            sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
