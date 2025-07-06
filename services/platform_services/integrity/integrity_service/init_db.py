#!/usr/bin/env python3
"""
Database initialization script for ACGS Persistent Audit Trail

This script creates the necessary database tables and initial data
for the persistent audit trail system.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import os
import logging
from pathlib import Path
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://acgs_user:acgs_password@localhost:5439/acgs_integrity")


async def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Extract database name from URL
        db_name = DATABASE_URL.split('/')[-1]
        base_url = DATABASE_URL.rsplit('/', 1)[0]
        
        # Connect to postgres database to create our database
        postgres_url = base_url.replace(f"/{db_name}", "/postgres")
        
        conn = await asyncpg.connect(postgres_url)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
            db_name
        )
        
        if not exists:
            await conn.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ Created database: {db_name}")
        else:
            logger.info(f"✅ Database already exists: {db_name}")
        
        await conn.close()
        
    except Exception as e:
        logger.warning(f"⚠️ Could not create database: {e}")


async def run_migration_scripts():
    """Run all migration scripts in the migrations directory."""
    try:
        # Create database if it doesn't exist
        await create_database_if_not_exists()
        
        # Connect to the target database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Find and run migration scripts
        migrations_dir = Path(__file__).parent / "migrations"
        
        if not migrations_dir.exists():
            logger.warning("⚠️ No migrations directory found")
            return
        
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        for migration_file in migration_files:
            logger.info(f"🔄 Running migration: {migration_file.name}")
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            try:
                await conn.execute(migration_sql)
                logger.info(f"✅ Migration completed: {migration_file.name}")
            except Exception as e:
                logger.error(f"❌ Migration failed: {migration_file.name} - {e}")
                raise
        
        await conn.close()
        logger.info("✅ All migrations completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration process failed: {e}")
        raise


async def test_database_connectivity():
    """Test database connectivity and basic operations."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test basic queries
        result = await conn.fetchval("SELECT 1")
        assert result == 1, "Basic query failed"
        
        # Test audit tables exist
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('audit_events', 'audit_blocks')
        """)
        
        table_names = [row['table_name'] for row in tables]
        assert 'audit_events' in table_names, "audit_events table not found"
        assert 'audit_blocks' in table_names, "audit_blocks table not found"
        
        # Test genesis block exists
        genesis_count = await conn.fetchval("SELECT COUNT(*) FROM audit_blocks WHERE block_number = 0")
        assert genesis_count == 1, "Genesis block not found"
        
        await conn.close()
        logger.info("✅ Database connectivity test passed")
        
    except Exception as e:
        logger.error(f"❌ Database connectivity test failed: {e}")
        raise


async def main():
    """Main initialization function."""
    logger.info("🚀 Starting ACGS Persistent Audit Trail Database Initialization")
    logger.info(f"📊 Constitutional Hash: cdd01ef066bc6cf2")
    logger.info(f"🔗 Database URL: {DATABASE_URL}")
    
    try:
        # Run migrations
        await run_migration_scripts()
        
        # Test connectivity
        await test_database_connectivity()
        
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("🔒 Persistent audit trail is ready for production use")
        
    except Exception as e:
        logger.error(f"💥 Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())