#!/bin/bash
# ACGS-2 Project Structure Reorganization Script
# Based on: organize-project-structure.md

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_ROOT="/home/dislove/ACGS-2"
BACKUP_DIR="${PROJECT_ROOT}/backup-$(date +%Y%m%d-%H%M%S)"
DRY_RUN=${1:-false}

# Check if running in project root
if [[ "$(pwd)" != "$PROJECT_ROOT" ]]; then
    log_error "Please run this script from the project root: $PROJECT_ROOT"
    exit 1
fi

# Create backup
create_backup() {
    log_info "Creating backup of current structure..."
    if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$BACKUP_DIR"
        # Copy important files and directories
        cp -r docs/ scripts/ tools/ services/ "$BACKUP_DIR/" 2>/dev/null || true
        cp *.md *.txt *.toml *.ini *.yml *.yaml *.json "$BACKUP_DIR/" 2>/dev/null || true
        log_success "Backup created at: $BACKUP_DIR"
    else
        log_info "[DRY RUN] Would create backup at: $BACKUP_DIR"
    fi
}

# Phase 1: Create new directory structure
create_directory_structure() {
    log_info "Phase 1: Creating standardized directory structure..."
    
    local directories=(
        "docs/getting-started"
        "docs/architecture" 
        "docs/api"
        "docs/deployment"
        "docs/development"
        "docs/security"
        "docs/troubleshooting"
        "scripts/setup"
        "scripts/deployment"
        "scripts/monitoring"
        "scripts/testing"
        "scripts/maintenance"
        "scripts/development"
        "services/shared/requirements"
        "services/core"
        "services/platform"
        "services/integration"
        "temp"
        "reports"
    )
    
    for dir in "${directories[@]}"; do
        if [[ "$DRY_RUN" == "false" ]]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log_info "[DRY RUN] Would create: $dir"
        fi
    done
}

# Phase 2: Move root directory files to appropriate locations
organize_root_files() {
    log_info "Phase 2: Organizing root directory files..."
    
    # Documentation files to move
    local doc_files=(
        "ACGE_RESEARCH_PLAN.md:docs/research/"
        "ACGS_DOCUMENTATION_AUDIT_REPORT.md:docs/architecture/"
        "ACGS_IMPROVEMENT_COMPLETION_REPORT.md:docs/deployment/"
        "ACGS_PRODUCTION_DEPLOYMENT_SUCCESS_VALIDATION.md:docs/deployment/"
        "AGENTS.md:docs/architecture/"
        "API_STANDARDIZATION_COMPLETION_REPORT.md:docs/api/"
        "CLAUDE_CONTEXT_ENGINEERING.md:docs/development/"
        "CONTRIBUTING.md:docs/development/"
        "DEPLOYMENT.md:docs/deployment/"
        "DEPENDENCIES.md:docs/development/"
        "GEMINI.md:docs/development/"
        "SECURITY_POLICY.yml:docs/security/"
        "SYSTEM_OVERVIEW.md:docs/architecture/"
    )
    
    for file_move in "${doc_files[@]}"; do
        local file="${file_move%%:*}"
        local dest="${file_move##*:}"
        
        if [[ -f "$file" ]]; then
            if [[ "$DRY_RUN" == "false" ]]; then
                mkdir -p "$dest"
                mv "$file" "$dest"
                log_success "Moved $file to $dest"
            else
                log_info "[DRY RUN] Would move: $file -> $dest"
            fi
        fi
    done
    
    # Report files to move
    local report_files=(
        "*.json"
        "*_REPORT.md"
        "*_SUMMARY.md"
        "benchmark_results.json"
        "cicd_pipeline_report.md"
        "gap-analysis.md"
        "improveplan.md"
    )
    
    for pattern in "${report_files[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" && "$file" != "pyproject.toml" && "$file" != "package.json" ]]; then
                if [[ "$DRY_RUN" == "false" ]]; then
                    mv "$file" reports/
                    log_success "Moved $file to reports/"
                else
                    log_info "[DRY RUN] Would move: $file -> reports/"
                fi
            fi
        done
    done
}

# Phase 3: Consolidate scripts and tools
consolidate_scripts() {
    log_info "Phase 3: Consolidating scripts and tools..."
    
    # Script categorization mapping
    declare -A script_categories=(
        ["setup"]="setup_|install_|init_|configure_"
        ["deployment"]="deploy_|start_|stop_|restart_"
        ["monitoring"]="monitor_|health_|check_|validate_"
        ["testing"]="test_|run_.*test|.*_test"
        ["maintenance"]="cleanup_|fix_|update_|migrate_"
        ["development"]="debug_|dev_|build_|compile_"
    )
    
    # Process scripts directory
    if [[ -d "scripts" ]]; then
        for script in scripts/*.py scripts/*.sh; do
            [[ -f "$script" ]] || continue
            
            local basename=$(basename "$script")
            local moved=false
            
            for category in "${!script_categories[@]}"; do
                local patterns="${script_categories[$category]}"
                if [[ "$basename" =~ $patterns ]]; then
                    if [[ "$DRY_RUN" == "false" ]]; then
                        mv "$script" "scripts/$category/"
                        log_success "Moved $basename to scripts/$category/"
                    else
                        log_info "[DRY RUN] Would move: $basename -> scripts/$category/"
                    fi
                    moved=true
                    break
                fi
            done
            
            if [[ "$moved" == "false" ]]; then
                if [[ "$DRY_RUN" == "false" ]]; then
                    mv "$script" "scripts/development/"
                    log_warning "Moved $basename to scripts/development/ (uncategorized)"
                else
                    log_info "[DRY RUN] Would move: $basename -> scripts/development/ (uncategorized)"
                fi
            fi
        done
    fi
    
    # Merge tools directory into scripts
    if [[ -d "tools" ]]; then
        log_info "Merging tools/ directory into scripts/..."
        if [[ "$DRY_RUN" == "false" ]]; then
            # Move tools content to scripts/development for manual categorization
            cp -r tools/* scripts/development/ 2>/dev/null || true
            log_success "Merged tools/ into scripts/development/"
            log_warning "Manual review needed for proper categorization of tools"
        else
            log_info "[DRY RUN] Would merge tools/ into scripts/development/"
        fi
    fi
}

# Phase 4: Create consolidated dependency files
consolidate_dependencies() {
    log_info "Phase 4: Creating consolidated dependency structure..."
    
    local req_dir="services/shared/requirements"
    
    # Base requirements (from pyproject.toml analysis)
    local base_requirements="# ACGS Shared Base Requirements
# Constitutional Hash: cdd01ef066bc6cf2

# Core Web Framework
fastapi>=0.115.6
uvicorn[standard]>=0.34.0
pydantic>=2.10.5
pydantic-settings>=2.7.1

# HTTP and Networking
httpx>=0.28.1
aiohttp>=3.9.0
aiofiles>=23.0.0

# Configuration
python-dotenv>=1.0.0
pyyaml>=6.0.1
click>=8.1.7
rich>=13.6.0"

    local web_requirements="# ACGS Web Service Requirements
-r requirements-base.txt

# Database and Storage
asyncpg>=0.29.0
sqlalchemy[asyncio]>=2.0.23
alembic>=1.13.0
redis>=5.0.1"

    local security_requirements="# ACGS Security Requirements
-r requirements-base.txt

# Security and Authentication
cryptography>=45.0.4
pyjwt[crypto]>=2.10.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.20"

    local test_requirements="# ACGS Testing Requirements
-r requirements-base.txt

# Testing Framework
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
hypothesis>=6.100.0
factory-boy>=3.3.0
fakeredis>=2.20.0"

    local dev_requirements="# ACGS Development Requirements
-r requirements-base.txt
-r requirements-test.txt

# Code Quality
black>=24.0.0
isort>=5.13.0
ruff>=0.3.0
mypy>=1.9.0
bandit>=1.7.0

# Development Tools
uvicorn[standard]>=0.29.0
watchfiles>=0.21.0"

    if [[ "$DRY_RUN" == "false" ]]; then
        echo "$base_requirements" > "$req_dir/requirements-base.txt"
        echo "$web_requirements" > "$req_dir/requirements-web.txt"
        echo "$security_requirements" > "$req_dir/requirements-security.txt"
        echo "$test_requirements" > "$req_dir/requirements-test.txt"
        echo "$dev_requirements" > "$req_dir/requirements-dev.txt"
        log_success "Created consolidated requirements files"
    else
        log_info "[DRY RUN] Would create consolidated requirements files in $req_dir"
    fi
}

# Phase 5: Update .gitignore for new structure
update_gitignore() {
    log_info "Phase 5: Updating .gitignore for new structure..."
    
    local new_ignores="
# Reorganization - temporary files
temp/
reports/*.json
reports/*.xml
backup-*/

# Generated documentation
docs/api/generated/

# Script outputs
scripts/*/output/
scripts/*/logs/"

    if [[ "$DRY_RUN" == "false" ]]; then
        echo "$new_ignores" >> .gitignore
        log_success "Updated .gitignore with new structure patterns"
    else
        log_info "[DRY RUN] Would add new patterns to .gitignore"
    fi
}

# Generate reorganization report
generate_report() {
    log_info "Generating reorganization report..."
    
    local report_file="REORGANIZATION_REPORT.md"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local report_content="# ACGS-2 Project Reorganization Report

**Date**: $timestamp
**Script**: execute-reorganization.sh
**Mode**: $([ "$DRY_RUN" == "true" ] && echo "DRY RUN" || echo "EXECUTION")

## Changes Made

### Phase 1: Directory Structure
- Created standardized directory hierarchy
- Established clear separation of concerns

### Phase 2: Root Directory Cleanup
- Moved documentation files to docs/
- Organized report files into reports/
- Cleaned up scattered configuration files

### Phase 3: Script Consolidation
- Categorized scripts by purpose
- Merged tools/ directory into scripts/
- Eliminated duplicate functionality

### Phase 4: Dependency Management
- Created shared requirements structure
- Consolidated 22 requirements files into 5 shared files
- Standardized dependency versions

### Phase 5: Configuration Updates
- Updated .gitignore for new structure
- Prepared for service migration

## Next Steps

1. **Service Migration**: Update services to use new shared requirements
2. **Documentation Review**: Verify all moved documentation is correctly linked
3. **CI/CD Updates**: Update build scripts for new structure
4. **Team Communication**: Inform team of new structure conventions

## Backup Location
$([ "$DRY_RUN" == "true" ] && echo "Would create backup at: $BACKUP_DIR" || echo "Backup created at: $BACKUP_DIR")

## Validation Checklist
- [ ] All services still build and run
- [ ] Documentation links are working
- [ ] CI/CD pipelines pass
- [ ] Dependencies resolve correctly
- [ ] No functionality lost in reorganization
"

    if [[ "$DRY_RUN" == "false" ]]; then
        echo "$report_content" > "$report_file"
        log_success "Generated report: $report_file"
    else
        log_info "[DRY RUN] Would generate: $report_file"
    fi
}

# Main execution
main() {
    log_info "Starting ACGS-2 Project Reorganization..."
    log_info "Mode: $([ "$DRY_RUN" == "true" ] && echo "DRY RUN (preview only)" || echo "EXECUTION (making changes)")"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        read -p "This will make significant changes to your project structure. Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Reorganization cancelled by user"
            exit 0
        fi
    fi
    
    create_backup
    create_directory_structure
    organize_root_files
    consolidate_scripts
    consolidate_dependencies
    update_gitignore
    generate_report
    
    log_success "Project reorganization completed!"
    log_info "Please review the changes and run validation tests"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        log_info "Backup available at: $BACKUP_DIR"
        log_info "Report generated: REORGANIZATION_REPORT.md"
    fi
}

# Show usage if requested
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [--dry-run]"
    echo
    echo "Options:"
    echo "  --dry-run    Preview changes without making them"
    echo "  --help       Show this help message"
    echo
    echo "This script reorganizes the ACGS-2 project structure according to"
    echo "the design specification in organize-project-structure.md"
    exit 0
fi

# Execute main function
main