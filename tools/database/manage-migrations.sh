#!/bin/bash

# ACGS-1 Database Migration Management Script
# Comprehensive database migration management for ACGS-1 Constitutional Governance System

set -euo pipefail

# Configuration
MIGRATIONS_DIR="migrations"
ROLLBACKS_DIR="migrations/rollbacks"
PYTHON_SCRIPT="scripts/database/migrate.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
ACGS-1 Database Migration Management Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    create      Create a new migration file
    status      Show migration status
    migrate     Apply pending migrations
    rollback    Rollback to specific version
    validate    Validate migration integrity
    backup      Create database backup
    restore     Restore from backup
    help        Show this help message

Options:
    --name NAME             Migration name (for create)
    --target VERSION        Target migration version
    --environment ENV       Environment (development, staging, production)
    --backup-file FILE      Backup file path
    --dry-run              Show what would be done without executing

Examples:
    $0 create --name "add_user_preferences_table"
    $0 status
    $0 migrate --environment staging
    $0 rollback --target 0001 --environment development
    $0 backup --environment production

Environment Variables:
    DATABASE_URL           Database connection URL
    BACKUP_S3_BUCKET      S3 bucket for backups (production)

EOF
}

# Parse command line arguments
parse_args() {
    COMMAND=""
    MIGRATION_NAME=""
    TARGET_VERSION=""
    ENVIRONMENT="development"
    BACKUP_FILE=""
    DRY_RUN=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            create|status|migrate|rollback|validate|backup|restore|help)
                COMMAND="$1"
                shift
                ;;
            --name)
                MIGRATION_NAME="$2"
                shift 2
                ;;
            --target)
                TARGET_VERSION="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --backup-file)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="--dry-run"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [[ -z "$COMMAND" ]]; then
        log_error "No command specified"
        show_help
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Python is installed
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if required Python packages are installed
    if ! python3 -c "import asyncpg, alembic" >/dev/null 2>&1; then
        log_error "Required Python packages not installed (asyncpg, alembic)"
        log_info "Run: pip install asyncpg alembic pyyaml"
        exit 1
    fi
    
    # Check if DATABASE_URL is set
    if [[ -z "${DATABASE_URL:-}" ]]; then
        log_error "DATABASE_URL environment variable is required"
        exit 1
    fi
    
    # Create directories if they don't exist
    mkdir -p "$MIGRATIONS_DIR" "$ROLLBACKS_DIR"
    
    log_success "Prerequisites check passed"
}

# Generate next migration version
get_next_version() {
    local latest_version="0000"
    
    if [[ -d "$MIGRATIONS_DIR" ]]; then
        for file in "$MIGRATIONS_DIR"/*.sql; do
            if [[ -f "$file" ]]; then
                filename=$(basename "$file" .sql)
                version=${filename:0:4}
                if [[ "$version" > "$latest_version" ]]; then
                    latest_version="$version"
                fi
            fi
        done
    fi
    
    # Increment version
    printf "%04d" $((10#$latest_version + 1))
}

# Create new migration
create_migration() {
    if [[ -z "$MIGRATION_NAME" ]]; then
        log_error "Migration name is required for create command"
        exit 1
    fi
    
    local version=$(get_next_version)
    local safe_name=$(echo "$MIGRATION_NAME" | tr ' ' '_' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_]//g')
    local migration_file="$MIGRATIONS_DIR/${version}_${safe_name}.sql"
    local rollback_file="$ROLLBACKS_DIR/rollback_${version}_${safe_name}.sql"
    
    log_info "Creating migration: $version - $MIGRATION_NAME"
    
    # Create migration file
    cat > "$migration_file" << EOF
-- Description: $MIGRATION_NAME
-- Version: $version
-- Author: $(git config user.name 2>/dev/null || echo "Unknown")
-- Date: $(date +%Y-%m-%d)

-- Set search path
SET search_path TO acgs, public;

-- TODO: Add your migration SQL here
-- Example:
-- CREATE TABLE example_table (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- CREATE INDEX idx_example_table_name ON example_table(name);
EOF
    
    # Create rollback file
    cat > "$rollback_file" << EOF
-- Rollback script for ${version}_${safe_name}.sql
-- This script reverses all changes made in the migration

-- Set search path
SET search_path TO acgs, public;

-- TODO: Add your rollback SQL here
-- Example:
-- DROP TABLE IF EXISTS example_table;
EOF
    
    log_success "Migration files created:"
    log_info "  Migration: $migration_file"
    log_info "  Rollback:  $rollback_file"
    log_warning "Please edit the files to add your SQL statements"
}

# Show migration status
show_status() {
    log_info "Getting migration status..."
    
    if [[ -n "$DRY_RUN" ]]; then
        log_info "DRY RUN: Would show migration status"
        return
    fi
    
    python3 "$PYTHON_SCRIPT" status
}

# Apply migrations
apply_migrations() {
    log_info "Applying migrations to $ENVIRONMENT environment..."
    
    if [[ -n "$DRY_RUN" ]]; then
        log_info "DRY RUN: Would apply migrations"
        return
    fi
    
    # Create backup for production/staging
    if [[ "$ENVIRONMENT" == "production" || "$ENVIRONMENT" == "staging" ]]; then
        create_backup
    fi
    
    # Apply migrations
    if [[ -n "$TARGET_VERSION" ]]; then
        python3 "$PYTHON_SCRIPT" migrate --target "$TARGET_VERSION"
    else
        python3 "$PYTHON_SCRIPT" migrate
    fi
    
    log_success "Migrations applied successfully"
}

# Rollback migrations
rollback_migrations() {
    if [[ -z "$TARGET_VERSION" ]]; then
        log_error "Target version is required for rollback"
        exit 1
    fi
    
    log_warning "Rolling back migrations to version $TARGET_VERSION in $ENVIRONMENT environment"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_warning "You are about to rollback PRODUCTION database!"
        read -p "Are you absolutely sure? Type 'yes' to continue: " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Rollback cancelled"
            exit 0
        fi
    fi
    
    if [[ -n "$DRY_RUN" ]]; then
        log_info "DRY RUN: Would rollback to version $TARGET_VERSION"
        return
    fi
    
    # Create backup before rollback
    if [[ "$ENVIRONMENT" == "production" || "$ENVIRONMENT" == "staging" ]]; then
        create_backup
    fi
    
    # Perform rollback
    python3 "$PYTHON_SCRIPT" rollback --target "$TARGET_VERSION"
    
    log_success "Rollback completed successfully"
}

# Validate migrations
validate_migrations() {
    log_info "Validating migration integrity..."
    
    if [[ -n "$DRY_RUN" ]]; then
        log_info "DRY RUN: Would validate migrations"
        return
    fi
    
    python3 "$PYTHON_SCRIPT" validate
    
    log_success "Migration validation completed"
}

# Create database backup
create_backup() {
    log_info "Creating database backup for $ENVIRONMENT..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_filename="acgs_backup_${ENVIRONMENT}_${timestamp}.sql"
    
    if [[ -n "$DRY_RUN" ]]; then
        log_info "DRY RUN: Would create backup: $backup_filename"
        return
    fi
    
    # Extract database connection details from DATABASE_URL
    local db_url="${DATABASE_URL}"
    local backup_path="/tmp/$backup_filename"
    
    # Create backup using pg_dump
    if command -v pg_dump >/dev/null 2>&1; then
        pg_dump "$db_url" > "$backup_path"
        
        # Upload to S3 for production
        if [[ "$ENVIRONMENT" == "production" && -n "${BACKUP_S3_BUCKET:-}" ]]; then
            if command -v aws >/dev/null 2>&1; then
                aws s3 cp "$backup_path" "s3://$BACKUP_S3_BUCKET/database-backups/$backup_filename"
                log_info "Backup uploaded to S3: s3://$BACKUP_S3_BUCKET/database-backups/$backup_filename"
            fi
        fi
        
        log_success "Backup created: $backup_path"
    else
        log_warning "pg_dump not available, skipping backup"
    fi
}

# Restore from backup
restore_backup() {
    if [[ -z "$BACKUP_FILE" ]]; then
        log_error "Backup file is required for restore"
        exit 1
    fi
    
    log_warning "Restoring database from backup: $BACKUP_FILE"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_warning "You are about to restore PRODUCTION database!"
        read -p "Are you absolutely sure? Type 'yes' to continue: " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Restore cancelled"
            exit 0
        fi
    fi
    
    if [[ -n "$DRY_RUN" ]]; then
        log_info "DRY RUN: Would restore from backup: $BACKUP_FILE"
        return
    fi
    
    # Restore using psql
    if command -v psql >/dev/null 2>&1; then
        psql "$DATABASE_URL" < "$BACKUP_FILE"
        log_success "Database restored from backup"
    else
        log_error "psql not available for restore"
        exit 1
    fi
}

# Main execution
main() {
    log_info "ACGS-1 Database Migration Management"
    log_info "Environment: $ENVIRONMENT"
    
    check_prerequisites
    
    case "$COMMAND" in
        "create")
            create_migration
            ;;
        "status")
            show_status
            ;;
        "migrate")
            apply_migrations
            ;;
        "rollback")
            rollback_migrations
            ;;
        "validate")
            validate_migrations
            ;;
        "backup")
            create_backup
            ;;
        "restore")
            restore_backup
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments and run
parse_args "$@"
main
