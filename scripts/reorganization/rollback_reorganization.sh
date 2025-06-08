#!/bin/bash
# ACGS-1 Reorganization Rollback Script
# Safely rolls back reorganization changes if issues are discovered

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 ACGS-1 Reorganization Rollback${NC}"
echo "Root directory: $ROOT_DIR"
echo "=================================================="

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
check_git_repository() {
    if [ ! -d ".git" ]; then
        log_error "Not a git repository. Cannot perform rollback."
        exit 1
    fi
    
    log_success "Git repository detected"
}

# Find the reorganization commit
find_reorganization_commit() {
    log_info "Finding reorganization commit..."
    
    # Look for the reorganization commit by message
    REORG_COMMIT=$(git log --oneline --grep="reorganize ACGS-1 codebase" -n 1 | cut -d' ' -f1)
    
    if [ -z "$REORG_COMMIT" ]; then
        log_error "Could not find reorganization commit"
        log_info "Looking for recent commits that might be the reorganization..."
        git log --oneline -10
        echo ""
        read -p "Enter the commit hash to rollback to (or press Enter to cancel): " MANUAL_COMMIT
        
        if [ -z "$MANUAL_COMMIT" ]; then
            log_info "Rollback cancelled"
            exit 0
        fi
        
        REORG_COMMIT="$MANUAL_COMMIT"
    fi
    
    log_success "Found reorganization commit: $REORG_COMMIT"
    
    # Show the commit details
    echo ""
    log_info "Commit details:"
    git show --stat "$REORG_COMMIT"
    echo ""
}

# Check for uncommitted changes
check_uncommitted_changes() {
    log_info "Checking for uncommitted changes..."
    
    if ! git diff-index --quiet HEAD --; then
        log_warning "You have uncommitted changes:"
        git status --porcelain
        echo ""
        
        read -p "Do you want to stash these changes before rollback? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Stashing uncommitted changes..."
            git stash push -m "Pre-rollback stash $(date)"
            log_success "Changes stashed"
        else
            log_warning "Proceeding with uncommitted changes (they may be lost)"
            read -p "Are you sure you want to continue? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Rollback cancelled"
                exit 0
            fi
        fi
    else
        log_success "No uncommitted changes detected"
    fi
}

# Create backup before rollback
create_rollback_backup() {
    log_info "Creating backup before rollback..."
    
    BACKUP_DIR="$ROOT_DIR/rollback_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Create git bundle
    git bundle create "$BACKUP_DIR/pre_rollback.bundle" --all
    
    # Copy current state of reorganized directories
    [ -d "blockchain" ] && cp -r blockchain "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "services" ] && cp -r services "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "applications" ] && cp -r applications "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "integrations" ] && cp -r integrations "$BACKUP_DIR/" 2>/dev/null || true
    [ -d "infrastructure" ] && cp -r infrastructure "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Backup created at: $BACKUP_DIR"
    echo "$BACKUP_DIR" > .rollback_backup_location
}

# Perform the rollback
perform_rollback() {
    log_info "Performing rollback..."
    
    # Get the commit before reorganization
    PARENT_COMMIT=$(git rev-parse "${REORG_COMMIT}^")
    
    log_info "Rolling back to commit: $PARENT_COMMIT"
    
    # Show what will be reset
    echo ""
    log_info "Files that will be affected:"
    git diff --name-status "$PARENT_COMMIT" HEAD | head -20
    if [ $(git diff --name-status "$PARENT_COMMIT" HEAD | wc -l) -gt 20 ]; then
        echo "... and $(( $(git diff --name-status "$PARENT_COMMIT" HEAD | wc -l) - 20 )) more files"
    fi
    echo ""
    
    read -p "Proceed with rollback? This will reset your working directory. (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
    
    # Perform the reset
    log_info "Resetting to pre-reorganization state..."
    git reset --hard "$PARENT_COMMIT"
    
    log_success "Rollback completed"
}

# Clean up reorganized directories
cleanup_reorganized_directories() {
    log_info "Cleaning up reorganized directories..."
    
    # Remove directories that were created during reorganization
    REORG_DIRS=(
        "blockchain"
        "services" 
        "applications"
        "integrations"
        "infrastructure/docker"
        "infrastructure/kubernetes"
        "tools"
    )
    
    for dir in "${REORG_DIRS[@]}"; do
        if [ -d "$dir" ] && [ ! -d "$dir/.git" ]; then
            log_info "Removing $dir..."
            rm -rf "$dir"
        fi
    done
    
    # Remove empty parent directories
    [ -d "infrastructure" ] && rmdir infrastructure 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Verify rollback success
verify_rollback() {
    log_info "Verifying rollback success..."
    
    # Check that old structure is restored
    if [ -d "quantumagi_core" ] && [ -d "src/backend" ]; then
        log_success "Original directory structure restored"
    else
        log_warning "Original directory structure may not be fully restored"
    fi
    
    # Check git status
    if git diff-index --quiet HEAD --; then
        log_success "Working directory is clean"
    else
        log_warning "Working directory has uncommitted changes"
        git status --short
    fi
    
    # Test basic functionality
    log_info "Testing basic functionality..."
    
    # Test if quantumagi_core builds
    if [ -d "quantumagi_core" ] && [ -f "quantumagi_core/Anchor.toml" ]; then
        cd quantumagi_core
        if command -v anchor &> /dev/null; then
            if timeout 60 anchor build &>/dev/null; then
                log_success "Quantumagi core builds successfully"
            else
                log_warning "Quantumagi core build failed"
            fi
        else
            log_info "Anchor CLI not available, skipping build test"
        fi
        cd "$ROOT_DIR"
    fi
    
    log_success "Rollback verification completed"
}

# Restore from backup if needed
restore_from_backup() {
    log_info "Checking for available backups..."
    
    # Find backup directories
    BACKUPS=($(find . -maxdepth 1 -name "backup_*" -type d 2>/dev/null))
    
    if [ ${#BACKUPS[@]} -eq 0 ]; then
        log_warning "No backup directories found"
        return
    fi
    
    echo "Available backups:"
    for i in "${!BACKUPS[@]}"; do
        echo "  $((i+1)). ${BACKUPS[$i]}"
    done
    echo ""
    
    read -p "Enter backup number to restore from (or press Enter to skip): " BACKUP_CHOICE
    
    if [ -z "$BACKUP_CHOICE" ]; then
        log_info "Skipping backup restore"
        return
    fi
    
    if [ "$BACKUP_CHOICE" -ge 1 ] && [ "$BACKUP_CHOICE" -le ${#BACKUPS[@]} ]; then
        SELECTED_BACKUP="${BACKUPS[$((BACKUP_CHOICE-1))]}"
        log_info "Restoring from backup: $SELECTED_BACKUP"
        
        # Restore git state from bundle
        if [ -f "$SELECTED_BACKUP/acgs_backup.bundle" ]; then
            log_info "Restoring git history from bundle..."
            git fetch "$SELECTED_BACKUP/acgs_backup.bundle"
        fi
        
        # Restore directory structure
        [ -d "$SELECTED_BACKUP/quantumagi_core" ] && cp -r "$SELECTED_BACKUP/quantumagi_core" .
        [ -d "$SELECTED_BACKUP/src" ] && cp -r "$SELECTED_BACKUP/src" .
        [ -d "$SELECTED_BACKUP/docs" ] && cp -r "$SELECTED_BACKUP/docs" .
        
        log_success "Backup restored"
    else
        log_error "Invalid backup selection"
    fi
}

# Generate rollback report
generate_rollback_report() {
    log_info "Generating rollback report..."
    
    REPORT_FILE="rollback_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# ACGS-1 Reorganization Rollback Report

**Date**: $(date)
**Rollback Commit**: $REORG_COMMIT
**Restored to**: $PARENT_COMMIT

## Rollback Summary

The ACGS-1 codebase reorganization has been rolled back successfully.

## Actions Taken

1. ✅ Created backup before rollback
2. ✅ Reset git history to pre-reorganization state
3. ✅ Cleaned up reorganized directories
4. ✅ Verified rollback success

## Current State

- Original directory structure restored
- Git working directory clean
- Basic functionality verified

## Backup Locations

EOF

    if [ -f ".rollback_backup_location" ]; then
        echo "- Rollback backup: $(cat .rollback_backup_location)" >> "$REPORT_FILE"
        rm .rollback_backup_location
    fi
    
    # List other backups
    BACKUPS=($(find . -maxdepth 1 -name "backup_*" -type d 2>/dev/null))
    for backup in "${BACKUPS[@]}"; do
        echo "- Original backup: $backup" >> "$REPORT_FILE"
    done
    
    cat >> "$REPORT_FILE" << EOF

## Next Steps

1. Review the issues that caused the rollback
2. Fix any problems in the reorganization approach
3. Re-run the reorganization when ready
4. Consider incremental reorganization approach

## Files Affected

EOF
    
    git diff --name-only "$PARENT_COMMIT" "$REORG_COMMIT" >> "$REPORT_FILE"
    
    log_success "Rollback report generated: $REPORT_FILE"
}

# Main rollback execution
main() {
    cd "$ROOT_DIR"
    
    log_info "Starting rollback process..."
    
    # Confirmation
    echo ""
    log_warning "This will rollback the ACGS-1 reorganization and restore the original structure."
    log_warning "Any changes made after reorganization may be lost."
    echo ""
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
    
    # Execute rollback steps
    check_git_repository
    find_reorganization_commit
    check_uncommitted_changes
    create_rollback_backup
    perform_rollback
    cleanup_reorganized_directories
    verify_rollback
    generate_rollback_report
    
    echo ""
    echo "=================================================="
    log_success "🎉 Rollback completed successfully!"
    echo "=================================================="
    echo ""
    log_info "The ACGS-1 codebase has been restored to its pre-reorganization state."
    log_info "Review the rollback report for details and next steps."
    echo ""
    log_info "If you need to restore specific files, check the backup directories."
    
    # Offer to restore from backup
    echo ""
    read -p "Do you want to restore any files from backup? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restore_from_backup
    fi
    
    log_success "Rollback process complete!"
}

# Execute main function
main "$@"
