"""
Database migrations for DGM service.
"""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..models import (
    Base,
)

logger = logging.getLogger(__name__)


class DGMMigrationManager:
    """Manages database migrations for DGM service."""

    def __init__(self, database_url: str):
        """Initialize migration manager."""
        self.database_url = database_url
        self.engine = None
        self.session_factory = None

    async def initialize(self):
        """Initialize database connection."""
        self.engine = create_async_engine(
            self.database_url, echo=False, pool_pre_ping=True
        )
        self.session_factory = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("DGM migration manager initialized")

    async def create_schema(self) -> dict[str, Any]:
        """Create DGM schema and tables."""
        result = {
            "schema_created": False,
            "tables_created": [],
            "indexes_created": [],
            "errors": [],
        }

        try:
            async with self.session_factory() as session:
                # Create DGM schema
                await session.execute(text("CREATE SCHEMA IF NOT EXISTS dgm"))
                await session.execute(
                    text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
                )
                await session.commit()
                result["schema_created"] = True
                logger.info("DGM schema created successfully")

                # Create all tables
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)

                result["tables_created"] = [
                    "dgm_archive",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "metric_aggregations",
                ]

                # Create additional indexes
                await self._create_performance_indexes(session)
                result["indexes_created"] = [
                    "idx_dgm_archive_status_timestamp",
                    "idx_performance_metrics_composite",
                    "idx_compliance_logs_service_level",
                    "idx_bandit_states_context_arm",
                    "idx_workspaces_status_created",
                ]

                await session.commit()
                logger.info("DGM tables and indexes created successfully")

        except Exception as e:
            logger.error(f"Error creating DGM schema: {e}")
            result["errors"].append(str(e))

        return result

    async def _create_performance_indexes(self, session: AsyncSession):
        """Create performance-optimized indexes."""
        indexes = [
            # Archive indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dgm_archive_status_timestamp
            ON dgm.dgm_archive (status, timestamp DESC)
            """,
            # Performance metrics indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_composite
            ON dgm.performance_metrics (service_name, metric_type, timestamp DESC)
            """,
            # Compliance logs indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_compliance_logs_service_level
            ON dgm.constitutional_compliance_logs (service_name, compliance_level, assessed_at DESC)
            """,
            # Bandit states indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bandit_states_context_arm
            ON dgm.bandit_states (context_key, arm_id, last_updated DESC)
            """,
            # Workspace indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_status_created
            ON dgm.improvement_workspaces (status, created_at DESC)
            """,
        ]

        for index_sql in indexes:
            try:
                await session.execute(text(index_sql))
                logger.info(f"Created index: {index_sql.split('idx_')[1].split()[0]}")
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")

    async def verify_schema(self) -> dict[str, Any]:
        """Verify DGM schema integrity."""
        verification_report = {
            "schema_exists": False,
            "tables": {},
            "indexes": {},
            "constitutional_compliance": False,
            "errors": [],
        }

        try:
            async with self.session_factory() as session:
                # Check schema existence
                result = await session.execute(
                    text(
                        "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'dgm'"
                    )
                )
                verification_report["schema_exists"] = result.scalar() > 0

                # Check table existence
                table_names = [
                    "dgm_archive",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "metric_aggregations",
                ]

                for table_name in table_names:
                    result = await session.execute(
                        text(
                            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'dgm' AND table_name = '{table_name}'"
                        )
                    )
                    table_exists = result.scalar() > 0
                    verification_report["tables"][table_name] = {
                        "exists": table_exists,
                        "status": "healthy" if table_exists else "missing",
                    }

                # Check constitutional compliance configuration
                try:
                    result = await session.execute(
                        text(
                            "SELECT COUNT(*) FROM dgm.system_configurations WHERE key = 'constitutional_hash'"
                        )
                    )
                    verification_report["constitutional_compliance"] = (
                        result.scalar() > 0
                    )
                except Exception:
                    verification_report["constitutional_compliance"] = False

        except Exception as e:
            logger.error(f"Schema verification error: {e}")
            verification_report["errors"].append(str(e))

        return verification_report

    async def rollback_schema(self) -> dict[str, Any]:
        """Rollback DGM schema (DANGEROUS - USE WITH CAUTION)."""
        rollback_result = {
            "tables_dropped": [],
            "schema_dropped": False,
            "errors": [],
            "warnings": [],
        }

        try:
            async with self.session_factory() as session:
                # Drop tables in reverse dependency order
                table_drop_order = [
                    "metric_aggregations",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "dgm_archive",
                ]

                for table_name in table_drop_order:
                    try:
                        await session.execute(
                            text(f"DROP TABLE IF EXISTS dgm.{table_name} CASCADE")
                        )
                        rollback_result["tables_dropped"].append(table_name)
                        logger.warning(f"Dropped table: dgm.{table_name}")
                    except Exception as e:
                        rollback_result["errors"].append(
                            f"Error dropping {table_name}: {e}"
                        )

                # Drop schema
                await session.execute(text("DROP SCHEMA IF EXISTS dgm CASCADE"))
                rollback_result["schema_dropped"] = True
                await session.commit()

                logger.warning("DGM schema completely rolled back")
                rollback_result["warnings"].append(
                    "All DGM data has been permanently deleted"
                )

        except Exception as e:
            logger.error(f"Rollback error: {e}")
            rollback_result["errors"].append(str(e))

        return rollback_result

    async def check_data_integrity(self) -> dict[str, Any]:
        """Perform comprehensive data integrity checks."""
        integrity_result = {
            "checks_passed": 0,
            "checks_failed": 0,
            "warnings": [],
            "errors": [],
            "details": {},
        }

        try:
            async with self.session_factory() as session:
                # Check 1: Constitutional hash consistency
                result = await session.execute(
                    text(
                        """
                SELECT COUNT(DISTINCT constitutional_hash) as hash_count,
                       COUNT(*) as total_records
                FROM (
                    SELECT constitutional_hash FROM dgm.dgm_archive
                    UNION ALL
                    SELECT constitutional_hash FROM dgm.performance_metrics
                    UNION ALL
                    SELECT constitutional_hash FROM dgm.constitutional_compliance_logs
                    UNION ALL
                    SELECT constitutional_hash FROM dgm.bandit_states
                    UNION ALL
                    SELECT constitutional_hash FROM dgm.improvement_workspaces
                    UNION ALL
                    SELECT constitutional_hash FROM dgm.system_configurations
                ) all_hashes
                """
                    )
                )
                hash_check = result.fetchone()

                if hash_check.hash_count == 1:
                    integrity_result["checks_passed"] += 1
                    integrity_result["details"]["constitutional_hash"] = "PASS"
                else:
                    integrity_result["checks_failed"] += 1
                    integrity_result["errors"].append(
                        f"Constitutional hash inconsistency: {hash_check.hash_count} different hashes found"
                    )
                    integrity_result["details"]["constitutional_hash"] = "FAIL"

                # Check 2: Foreign key integrity
                result = await session.execute(
                    text(
                        """
                SELECT COUNT(*) as orphaned_metrics
                FROM dgm.performance_metrics pm
                LEFT JOIN dgm.dgm_archive da ON pm.improvement_id = da.improvement_id
                WHERE pm.improvement_id IS NOT NULL AND da.improvement_id IS NULL
                """
                    )
                )
                orphaned_metrics = result.scalar()

                if orphaned_metrics == 0:
                    integrity_result["checks_passed"] += 1
                    integrity_result["details"]["foreign_key_integrity"] = "PASS"
                else:
                    integrity_result["checks_failed"] += 1
                    integrity_result["errors"].append(
                        f"Found {orphaned_metrics} orphaned performance metrics"
                    )
                    integrity_result["details"]["foreign_key_integrity"] = "FAIL"

                # Check 3: Compliance score ranges
                result = await session.execute(
                    text(
                        """
                SELECT COUNT(*) as invalid_scores
                FROM dgm.constitutional_compliance_logs
                WHERE compliance_score < 0.0 OR compliance_score > 1.0
                """
                    )
                )
                invalid_scores = result.scalar()

                if invalid_scores == 0:
                    integrity_result["checks_passed"] += 1
                    integrity_result["details"]["compliance_score_range"] = "PASS"
                else:
                    integrity_result["checks_failed"] += 1
                    integrity_result["errors"].append(
                        f"Found {invalid_scores} compliance scores outside valid range [0.0, 1.0]"
                    )
                    integrity_result["details"]["compliance_score_range"] = "FAIL"

                # Check 4: Timestamp consistency
                result = await session.execute(
                    text(
                        """
                SELECT COUNT(*) as future_timestamps
                FROM dgm.dgm_archive
                WHERE created_at > NOW() OR updated_at > NOW()
                """
                    )
                )
                future_timestamps = result.scalar()

                if future_timestamps == 0:
                    integrity_result["checks_passed"] += 1
                    integrity_result["details"]["timestamp_consistency"] = "PASS"
                else:
                    integrity_result["warnings"].append(
                        f"Found {future_timestamps} records with future timestamps"
                    )
                    integrity_result["details"]["timestamp_consistency"] = "WARNING"

                logger.info(
                    f"Data integrity check completed: {integrity_result['checks_passed']} passed, {integrity_result['checks_failed']} failed"
                )

        except Exception as e:
            logger.error(f"Data integrity check error: {e}")
            integrity_result["errors"].append(str(e))

        return integrity_result

    async def migrate_data(self, source_data: dict[str, Any] = None) -> dict[str, Any]:
        """Migrate data from external sources or initialize with defaults."""
        migration_result = {
            "configurations_created": 0,
            "baseline_metrics_created": 0,
            "default_bandit_states_created": 0,
            "errors": [],
        }

        try:
            async with self.session_factory() as session:
                # Initialize default system configurations
                default_configs = [
                    {
                        "key": "constitutional_hash",
                        "value": "cdd01ef066bc6cf2",
                        "value_type": "string",
                        "description": "ACGS constitutional compliance hash",
                        "category": "compliance",
                        "is_readonly": True,
                    },
                    {
                        "key": "max_improvement_attempts",
                        "value": "10",
                        "value_type": "integer",
                        "description": "Maximum improvement attempts per cycle",
                        "category": "safety",
                    },
                    {
                        "key": "safety_threshold",
                        "value": "0.8",
                        "value_type": "float",
                        "description": "Minimum safety threshold for improvements",
                        "category": "safety",
                    },
                    {
                        "key": "bandit_exploration_rate",
                        "value": "0.1",
                        "value_type": "float",
                        "description": "Conservative exploration rate for bandit algorithms",
                        "category": "learning",
                    },
                ]

                for config in default_configs:
                    await session.execute(
                        text(
                            """
                        INSERT INTO dgm.system_configurations
                        (key, value, value_type, description, category, is_readonly, constitutional_hash)
                        VALUES (:key, :value, :value_type, :description, :category, :is_readonly, :constitutional_hash)
                        ON CONFLICT (key) DO NOTHING
                        """
                        ),
                        {**config, "constitutional_hash": "cdd01ef066bc6cf2"},
                    )
                    migration_result["configurations_created"] += 1

                await session.commit()
                logger.info(
                    f"Created {migration_result['configurations_created']} default configurations"
                )

        except Exception as e:
            logger.error(f"Data migration error: {e}")
            migration_result["errors"].append(str(e))

        return migration_result

    async def backup_schema(self, backup_name: str = None) -> dict[str, Any]:
        """Create a backup of the current DGM schema."""
        if not backup_name:
            from datetime import datetime

            backup_name = f"dgm_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        backup_result = {
            "backup_name": backup_name,
            "tables_backed_up": [],
            "backup_location": f"dgm_backups.{backup_name}",
            "errors": [],
        }

        try:
            async with self.session_factory() as session:
                # Create backup schema
                await session.execute(text("CREATE SCHEMA IF NOT EXISTS dgm_backups"))
                await session.execute(
                    text(f"CREATE SCHEMA IF NOT EXISTS dgm_backups.{backup_name}")
                )

                # Backup each table
                tables = [
                    "dgm_archive",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "metric_aggregations",
                ]

                for table in tables:
                    try:
                        await session.execute(
                            text(
                                f"""
                        CREATE TABLE dgm_backups.{backup_name}.{table} AS
                        SELECT * FROM dgm.{table}
                        """
                            )
                        )
                        backup_result["tables_backed_up"].append(table)
                    except Exception as e:
                        backup_result["errors"].append(f"Error backing up {table}: {e}")

                await session.commit()
                logger.info(f"Schema backup created: {backup_name}")

        except Exception as e:
            logger.error(f"Backup error: {e}")
            backup_result["errors"].append(str(e))

        return backup_result

    async def restore_from_backup(self, backup_name: str) -> dict[str, Any]:
        """Restore DGM schema from a backup."""
        restore_result = {
            "backup_name": backup_name,
            "tables_restored": [],
            "errors": [],
        }

        try:
            async with self.session_factory() as session:
                # Verify backup exists
                result = await session.execute(
                    text(
                        f"""
                SELECT COUNT(*) FROM information_schema.schemata
                WHERE schema_name = 'dgm_backups.{backup_name}'
                """
                    )
                )

                if result.scalar() == 0:
                    raise ValueError(f"Backup {backup_name} not found")

                # Restore each table
                tables = [
                    "dgm_archive",
                    "performance_metrics",
                    "constitutional_compliance_logs",
                    "bandit_states",
                    "improvement_workspaces",
                    "system_configurations",
                    "metric_aggregations",
                ]

                for table in tables:
                    try:
                        # Clear existing data
                        await session.execute(
                            text(f"TRUNCATE TABLE dgm.{table} CASCADE")
                        )

                        # Restore from backup
                        await session.execute(
                            text(
                                f"""
                        INSERT INTO dgm.{table}
                        SELECT * FROM dgm_backups.{backup_name}.{table}
                        """
                            )
                        )
                        restore_result["tables_restored"].append(table)
                    except Exception as e:
                        restore_result["errors"].append(f"Error restoring {table}: {e}")

                await session.commit()
                logger.info(f"Schema restored from backup: {backup_name}")

        except Exception as e:
            logger.error(f"Restore error: {e}")
            restore_result["errors"].append(str(e))

        return restore_result

    async def cleanup(self):
        """Clean up database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("DGM migration manager cleaned up")


async def run_dgm_migrations(
    database_url: str, operation: str = "create"
) -> dict[str, Any]:
    """Run DGM database migrations."""
    manager = DGMMigrationManager(database_url)
    await manager.initialize()

    try:
        if operation == "create":
            result = await manager.create_schema()
            if result.get("schema_created"):
                data_result = await manager.migrate_data()
                result.update(data_result)
            return result
        if operation == "verify":
            return await manager.verify_schema()
        if operation == "rollback":
            return await manager.rollback_schema()
        if operation.startswith("backup"):
            backup_name = operation.split(":")[-1] if ":" in operation else None
            return await manager.backup_schema(backup_name)
        if operation.startswith("restore"):
            backup_name = operation.split(":")[-1]
            return await manager.restore_from_backup(backup_name)
        raise ValueError(f"Unknown operation: {operation}")
    finally:
        await manager.cleanup()
