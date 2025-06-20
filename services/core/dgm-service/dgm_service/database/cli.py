#!/usr/bin/env python3
"""
CLI interface for DGM database migrations.
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from typing import Dict, Any

from .migrations import run_dgm_migrations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from environment or config."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db"
    )


async def run_migration_command(operation: str, database_url: str) -> Dict[str, Any]:
    """Run a migration command and return results."""
    try:
        result = await run_dgm_migrations(database_url, operation)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return {"success": False, "error": str(e)}


def print_result(result: Dict[str, Any], operation: str):
    """Pretty print migration results."""
    if result["success"]:
        print(f"✅ {operation.upper()} completed successfully")

        if "result" in result:
            data = result["result"]

            # Print summary based on operation
            if operation == "create":
                if data.get("schema_created"):
                    print(f"   📁 Schema created")
                if data.get("tables_created"):
                    print(f"   📋 Tables created: {len(data['tables_created'])}")
                if data.get("indexes_created"):
                    print(f"   🔍 Indexes created: {len(data['indexes_created'])}")
                if data.get("configurations_created", 0) > 0:
                    print(f"   ⚙️  Configurations initialized: {data['configurations_created']}")

            elif operation == "verify":
                if data.get("schema_exists"):
                    print(f"   📁 Schema exists: ✅")
                else:
                    print(f"   📁 Schema exists: ❌")

                tables = data.get("tables", {})
                healthy_tables = sum(1 for t in tables.values() if t.get("status") == "healthy")
                print(f"   📋 Tables healthy: {healthy_tables}/{len(tables)}")

                if data.get("constitutional_compliance"):
                    print(f"   🏛️  Constitutional compliance: ✅")
                else:
                    print(f"   🏛️  Constitutional compliance: ❌")

            elif operation == "rollback":
                if data.get("schema_dropped"):
                    print(f"   🗑️  Schema dropped: ✅")
                dropped_tables = len(data.get("tables_dropped", []))
                print(f"   📋 Tables dropped: {dropped_tables}")

            elif operation.startswith("backup"):
                backup_name = data.get("backup_name", "unknown")
                backed_up = len(data.get("tables_backed_up", []))
                print(f"   💾 Backup '{backup_name}' created")
                print(f"   📋 Tables backed up: {backed_up}")

            elif operation.startswith("restore"):
                backup_name = data.get("backup_name", "unknown")
                restored = len(data.get("tables_restored", []))
                print(f"   🔄 Restored from backup '{backup_name}'")
                print(f"   📋 Tables restored: {restored}")

            # Print errors and warnings
            if data.get("errors"):
                print(f"   ⚠️  Errors: {len(data['errors'])}")
                for error in data["errors"]:
                    print(f"      - {error}")

            if data.get("warnings"):
                print(f"   ⚠️  Warnings: {len(data['warnings'])}")
                for warning in data["warnings"]:
                    print(f"      - {warning}")
    else:
        print(f"❌ {operation.upper()} failed")
        print(f"   Error: {result['error']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DGM Database Migration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create                    # Create schema and tables
  %(prog)s verify                    # Verify schema integrity
  %(prog)s rollback                  # Drop all DGM tables (DANGEROUS!)
  %(prog)s backup                    # Create backup with auto-generated name
  %(prog)s backup:my_backup          # Create backup with specific name
  %(prog)s restore:my_backup         # Restore from specific backup
  %(prog)s --database-url postgresql://... create
        """
    )

    parser.add_argument(
        "operation",
        choices=["create", "verify", "rollback", "backup", "restore"],
        help="Migration operation to perform"
    )

    parser.add_argument(
        "--database-url",
        default=None,
        help="Database URL (default: from DATABASE_URL env var)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get database URL
    database_url = args.database_url or get_database_url()

    # Handle backup/restore operations with names
    operation = args.operation
    if ":" in operation:
        op_type, op_name = operation.split(":", 1)
        if op_type not in ["backup", "restore"]:
            print(f"❌ Invalid operation format: {operation}")
            sys.exit(1)

    # Confirm dangerous operations
    if operation == "rollback":
        print("⚠️  WARNING: This will permanently delete all DGM data!")
        confirm = input("Type 'DELETE ALL DATA' to confirm: ")
        if confirm != "DELETE ALL DATA":
            print("❌ Operation cancelled")
            sys.exit(1)

    # Run migration
    try:
        result = asyncio.run(run_migration_command(operation, database_url))

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(result, operation)

        # Exit with error code if operation failed
        if not result["success"]:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()