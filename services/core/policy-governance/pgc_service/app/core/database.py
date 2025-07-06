"""
Database module for PGC Service.

This module provides real database connectivity and operations for the
Policy Governance Compiler (PGC) service, replacing mock implementations
with actual SQLAlchemy-based database operations.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from typing import Any, Optional

# Import real database implementation
from .real_database import (
    CONSTITUTIONAL_HASH,
    RealDatabaseManager,
    close_real_database,
    get_real_database_manager,
    initialize_real_database,
)

logger = logging.getLogger(__name__)


class DatabaseManager(RealDatabaseManager):
    """Database manager for PGC service with real database operations."""

    def __init__(self, connection_string: Optional[str] = None):
        """Initialize real database manager."""
        super().__init__(connection_string)
        logger.info("Real database manager initialized for PGC service")

    async def store_policy(self, policy_data: dict[str, Any]) -> bool:
        """Store policy data in database."""
        try:
            query = """
                INSERT INTO policies (name, content, version, created_at, constitutional_hash)
                VALUES (:name, :content, :version, :created_at, :constitutional_hash)
            """
            params = {
                "name": policy_data.get("name"),
                "content": policy_data.get("content"),
                "version": policy_data.get("version", "1.0"),
                "created_at": policy_data.get("created_at"),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            result = await self.execute_query(query, params)
            logger.info(f"Policy stored successfully: {policy_data.get('name')}")
            return True

        except Exception as e:
            logger.error(f"Failed to store policy: {e}")
            return False

    async def get_policy(self, policy_name: str) -> Optional[dict[str, Any]]:
        """Retrieve policy by name."""
        try:
            query = """
                SELECT name, content, version, created_at, constitutional_hash
                FROM policies
                WHERE name = :name AND constitutional_hash = :constitutional_hash
            """
            params = {"name": policy_name, "constitutional_hash": CONSTITUTIONAL_HASH}

            result = await self.execute_query(query, params)
            if result:
                logger.info(f"Policy retrieved: {policy_name}")
                return result[0]
            else:
                logger.warning(f"Policy not found: {policy_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve policy {policy_name}: {e}")
            return None

    async def list_policies(self) -> list[dict[str, Any]]:
        """List all policies."""
        try:
            query = """
                SELECT name, version, created_at
                FROM policies
                WHERE constitutional_hash = :constitutional_hash
                ORDER BY created_at DESC
            """
            params = {"constitutional_hash": CONSTITUTIONAL_HASH}

            result = await self.execute_query(query, params)
            logger.info(f"Retrieved {len(result)} policies")
            return result

        except Exception as e:
            logger.error(f"Failed to list policies: {e}")
            return []

    async def update_policy(
        self, policy_name: str, policy_data: dict[str, Any]
    ) -> bool:
        """Update existing policy."""
        try:
            query = """
                UPDATE policies
                SET content = :content, version = :version, updated_at = :updated_at
                WHERE name = :name AND constitutional_hash = :constitutional_hash
            """
            params = {
                "name": policy_name,
                "content": policy_data.get("content"),
                "version": policy_data.get("version"),
                "updated_at": policy_data.get("updated_at"),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

            result = await self.execute_query(query, params)
            affected_rows = result[0].get("affected_rows", 0) if result else 0

            if affected_rows > 0:
                logger.info(f"Policy updated successfully: {policy_name}")
                return True
            else:
                logger.warning(f"No policy found to update: {policy_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to update policy {policy_name}: {e}")
            return False

    async def delete_policy(self, policy_name: str) -> bool:
        """Delete policy by name."""
        try:
            query = """
                DELETE FROM policies
                WHERE name = :name AND constitutional_hash = :constitutional_hash
            """
            params = {"name": policy_name, "constitutional_hash": CONSTITUTIONAL_HASH}

            result = await self.execute_query(query, params)
            affected_rows = result[0].get("affected_rows", 0) if result else 0

            if affected_rows > 0:
                logger.info(f"Policy deleted successfully: {policy_name}")
                return True
            else:
                logger.warning(f"No policy found to delete: {policy_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete policy {policy_name}: {e}")
            return False


# Global database manager instance (enhanced with real implementation)
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get or create real database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def initialize_database() -> bool:
    """Initialize real database connection."""
    db_manager = get_database_manager()
    success = await db_manager.connect()

    if success:
        # Create tables if they don't exist
        await _ensure_policy_tables_exist(db_manager)
        logger.info("Database initialized with real implementation")
    else:
        logger.error("Failed to initialize real database")

    return success


async def close_database() -> None:
    """Close real database connection."""
    global _db_manager
    if _db_manager:
        await _db_manager.disconnect()
        _db_manager = None
        logger.info("Real database connection closed")


async def _ensure_policy_tables_exist(db_manager: DatabaseManager) -> None:
    """Ensure policy tables exist in the database."""
    try:
        # Create policies table if it doesn't exist
        create_table_query = """
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                content TEXT NOT NULL,
                version VARCHAR(50) DEFAULT '1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                constitutional_hash VARCHAR(255) NOT NULL,
                INDEX idx_name (name),
                INDEX idx_constitutional_hash (constitutional_hash)
            )
        """

        # For PostgreSQL, adjust the query
        if "postgresql" in db_manager.database_url:
            create_table_query = """
                CREATE TABLE IF NOT EXISTS policies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    version VARCHAR(50) DEFAULT '1.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    constitutional_hash VARCHAR(255) NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_policies_name ON policies(name);
                CREATE INDEX IF NOT EXISTS idx_policies_constitutional_hash ON policies(constitutional_hash);
            """

        await db_manager.execute_query(create_table_query)
        logger.info("Policy tables ensured to exist")

    except Exception as e:
        logger.error(f"Failed to create policy tables: {e}")


# Backward compatibility aliases
get_real_database_manager = get_database_manager
initialize_real_database = initialize_database
close_real_database = close_database
