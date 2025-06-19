"""
Database Migration Scripts

Database schema creation and migration utilities for ACGS-PGP v8.
"""

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .connection import DatabaseManager, get_database_manager
from .models import Base

logger = logging.getLogger(__name__)


async def create_tables(db_manager: DatabaseManager | None = None) -> bool:
    """
    Create all database tables for ACGS-PGP v8.

    Args:
        db_manager: Database manager instance (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    if db_manager is None:
        db_manager = get_database_manager()

    try:
        # Initialize async engine
        db_manager.initialize_async_engine()

        # Create all tables
        async with db_manager._async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ All database tables created successfully")
        return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error creating tables: {e}")
        return False


async def drop_tables(db_manager: DatabaseManager | None = None) -> bool:
    """
    Drop all database tables for ACGS-PGP v8.

    Args:
        db_manager: Database manager instance (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    if db_manager is None:
        db_manager = get_database_manager()

    try:
        # Initialize async engine
        db_manager.initialize_async_engine()

        # Drop all tables
        async with db_manager._async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        logger.info("✅ All database tables dropped successfully")
        return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error dropping tables: {e}")
        return False


async def create_indexes(db_manager: DatabaseManager | None = None) -> bool:
    """
    Create additional database indexes for performance optimization.

    Args:
        db_manager: Database manager instance (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    if db_manager is None:
        db_manager = get_database_manager()

    additional_indexes = [
        # Performance indexes for policy generations
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_generation_performance
        ON policy_generations (generation_time_ms, constitutional_compliance_score)
        """,
        # Composite index for audit logs
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_user_timestamp
        ON audit_logs (user_id, timestamp DESC)
        """,
        # Index for stabilizer execution performance analysis
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stabilizer_execution_errors
        ON stabilizer_executions (errors_detected, errors_corrected, started_at)
        """,
        # Index for system diagnostics health monitoring
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_diagnostic_health_timestamp
        ON system_diagnostics (overall_health_score, diagnostic_timestamp DESC)
        """,
        # Index for LSU records usage tracking
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lsu_record_usage
        ON lsu_records (usage_count DESC, last_used_at DESC)
        """,
        # Partial index for active executions
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stabilizer_execution_active
        ON stabilizer_executions (started_at)
        WHERE completed_at IS NULL
        """,
        # Index for constitutional compliance monitoring
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_constitutional_compliance
        ON policy_generations (constitutional_hash, constitutional_compliance_score)
        """,
    ]

    try:
        async with db_manager.async_session_scope() as session:
            for index_sql in additional_indexes:
                try:
                    await session.execute(text(index_sql))
                    logger.info(f"✅ Created index: {index_sql.split()[5]}")
                except SQLAlchemyError as e:
                    logger.warning(f"⚠️ Index creation failed (may already exist): {e}")

            await session.commit()

        logger.info("✅ Additional database indexes created successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create additional indexes: {e}")
        return False


async def insert_default_configuration(
    db_manager: DatabaseManager | None = None,
) -> bool:
    """
    Insert default configuration settings for ACGS-PGP v8.

    Args:
        db_manager: Database manager instance (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    if db_manager is None:
        db_manager = get_database_manager()

    from datetime import datetime

    from .models import ConfigurationSetting

    default_configs = [
        {
            "key": "constitutional_hash",
            "value": "cdd01ef066bc6cf2",
            "value_type": "string",
            "description": "Constitutional governance hash for compliance validation",
            "category": "constitutional",
            "is_readonly": True,
        },
        {
            "key": "max_policy_length",
            "value": "5000",
            "value_type": "integer",
            "description": "Maximum length for generated policies",
            "category": "generation_engine",
        },
        {
            "key": "min_constitutional_compliance",
            "value": "0.8",
            "value_type": "float",
            "description": "Minimum constitutional compliance score required",
            "category": "constitutional",
        },
        {
            "key": "consensus_threshold",
            "value": "0.7",
            "value_type": "float",
            "description": "Consensus threshold for representation voting",
            "category": "generation_engine",
        },
        {
            "key": "fault_tolerance_level",
            "value": "2",
            "value_type": "integer",
            "description": "Fault tolerance level for error correction",
            "category": "stabilizer",
        },
        {
            "key": "response_time_target_ms",
            "value": "500",
            "value_type": "integer",
            "description": "Target response time in milliseconds",
            "category": "performance",
        },
        {
            "key": "enable_quantum_enhancement",
            "value": "true",
            "value_type": "boolean",
            "description": "Enable quantum-inspired enhancements",
            "category": "quantum",
        },
        {
            "key": "audit_trail_enabled",
            "value": "true",
            "value_type": "boolean",
            "description": "Enable comprehensive audit trail logging",
            "category": "security",
        },
    ]

    try:
        async with db_manager.async_session_scope() as session:
            for config_data in default_configs:
                # Check if configuration already exists
                existing = await session.execute(
                    text("SELECT id FROM configuration_settings WHERE key = :key"),
                    {"key": config_data["key"]},
                )

                if existing.fetchone() is None:
                    config = ConfigurationSetting(
                        key=config_data["key"],
                        value=config_data["value"],
                        value_type=config_data["value_type"],
                        description=config_data["description"],
                        category=config_data["category"],
                        is_readonly=config_data.get("is_readonly", False),
                        constitutional_hash="cdd01ef066bc6cf2",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(config)
                    logger.info(f"✅ Added default configuration: {config_data['key']}")
                else:
                    logger.info(f"⚠️ Configuration already exists: {config_data['key']}")

            await session.commit()

        logger.info("✅ Default configuration settings inserted successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to insert default configuration: {e}")
        return False


async def run_migrations(db_manager: DatabaseManager | None = None) -> bool:
    """
    Run complete database migration process.

    Args:
        db_manager: Database manager instance (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    if db_manager is None:
        db_manager = get_database_manager()

    logger.info("🚀 Starting ACGS-PGP v8 database migration...")

    try:
        # Step 1: Create tables
        if not await create_tables(db_manager):
            return False

        # Step 2: Create additional indexes
        if not await create_indexes(db_manager):
            logger.warning("⚠️ Some indexes failed to create, continuing...")

        # Step 3: Insert default configuration
        if not await insert_default_configuration(db_manager):
            logger.warning("⚠️ Default configuration insertion failed, continuing...")

        # Step 4: Verify database health
        health_status = await db_manager.health_check()
        if health_status["status"] != "healthy":
            logger.error("❌ Database health check failed after migration")
            return False

        logger.info("🎉 ACGS-PGP v8 database migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        return False


async def verify_schema(db_manager: DatabaseManager | None = None) -> dict:
    """
    Verify database schema integrity and return status report.

    Args:
        db_manager: Database manager instance (optional)

    Returns:
        dict: Schema verification report
    """
    if db_manager is None:
        db_manager = get_database_manager()

    verification_report = {
        "status": "healthy",
        "tables": {},
        "indexes": {},
        "constitutional_hash": "cdd01ef066bc6cf2",
        "timestamp": None,
    }

    try:
        async with db_manager.async_session_scope() as session:
            # Check table existence
            table_names = [
                "policy_generations",
                "stabilizer_executions",
                "system_diagnostics",
                "lsu_records",
                "configuration_settings",
                "audit_logs",
            ]

            for table_name in table_names:
                result = await session.execute(
                    text(
                        f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
                    )
                )
                table_exists = result.scalar() > 0
                verification_report["tables"][table_name] = {
                    "exists": table_exists,
                    "status": "healthy" if table_exists else "missing",
                }

            # Check constitutional hash configuration
            config_result = await session.execute(
                text("SELECT value FROM configuration_settings WHERE key = 'constitutional_hash'")
            )
            config_hash = config_result.scalar()

            if config_hash != "cdd01ef066bc6cf2":
                verification_report["status"] = "unhealthy"
                verification_report["constitutional_hash_mismatch"] = {
                    "expected": "cdd01ef066bc6cf2",
                    "found": config_hash,
                }

            from datetime import datetime

            verification_report["timestamp"] = datetime.utcnow().isoformat()

    except Exception as e:
        verification_report["status"] = "unhealthy"
        verification_report["error"] = str(e)
        logger.error(f"Schema verification failed: {e}")

    return verification_report
