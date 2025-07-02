#!/bin/bash

# ACGS-1 GitHub Environments Setup Script
# This script sets up GitHub environments with appropriate protection rules

set -euo pipefail

# Configuration
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-CA-git-com-co}"
REPO_NAME="${GITHUB_REPOSITORY_NAME:-ACGS}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [ -z "$GITHUB_TOKEN" ]; then
        log_error "GITHUB_TOKEN environment variable is required"
        exit 1
    fi
    
    if ! command -v curl >/dev/null 2>&1; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v jq >/dev/null 2>&1; then
        log_error "jq is required but not installed"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# GitHub API helper function
github_api() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    local url="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}${endpoint}"
    
    if [ -n "$data" ]; then
        curl -s -X "$method" \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url"
    else
        curl -s -X "$method" \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "$url"
    fi
}

# Create or update environment
create_environment() {
    local env_name="$1"
    local protection_rules="$2"
    
    log_info "Creating/updating environment: $env_name"
    
    # Create environment
    local env_data="{\"wait_timer\": 0, \"prevent_self_review\": true, \"reviewers\": [], \"deployment_branch_policy\": null}"
    
    local response=$(github_api "PUT" "/environments/$env_name" "$env_data")
    
    if echo "$response" | jq -e '.name' >/dev/null 2>&1; then
        log_success "Environment $env_name created/updated successfully"
    else
        log_error "Failed to create environment $env_name"
        echo "$response" | jq '.'
        return 1
    fi
    
    # Apply protection rules if provided
    if [ -n "$protection_rules" ]; then
        log_info "Applying protection rules to $env_name"
        local protection_response=$(github_api "PUT" "/environments/$env_name" "$protection_rules")
        
        if echo "$protection_response" | jq -e '.protection_rules' >/dev/null 2>&1; then
            log_success "Protection rules applied to $env_name"
        else
            log_warning "Failed to apply some protection rules to $env_name"
        fi
    fi
}

# Setup development environment
setup_development_environment() {
    log_info "Setting up development environment..."
    
    local protection_rules='{
        "wait_timer": 0,
        "prevent_self_review": false,
        "reviewers": [],
        "deployment_branch_policy": {
            "protected_branches": false,
            "custom_branch_policies": true
        }
    }'
    
    create_environment "development" "$protection_rules"
}

# Setup staging environment
setup_staging_environment() {
    log_info "Setting up staging environment..."
    
    local protection_rules='{
        "wait_timer": 5,
        "prevent_self_review": true,
        "reviewers": [
            {
                "type": "Team",
                "id": "development-team"
            }
        ],
        "deployment_branch_policy": {
            "protected_branches": true,
            "custom_branch_policies": false
        }
    }'
    
    create_environment "staging" "$protection_rules"
}

# Setup production environment
setup_production_environment() {
    log_info "Setting up production environment..."
    
    local protection_rules='{
        "wait_timer": 30,
        "prevent_self_review": true,
        "reviewers": [
            {
                "type": "Team",
                "id": "platform-team"
            },
            {
                "type": "Team", 
                "id": "security-team"
            }
        ],
        "deployment_branch_policy": {
            "protected_branches": true,
            "custom_branch_policies": false
        }
    }'
    
    create_environment "production" "$protection_rules"
}

# Setup approval environments
setup_approval_environments() {
    log_info "Setting up approval environments..."
    
    # Staging approval environment
    local staging_approval_rules='{
        "wait_timer": 0,
        "prevent_self_review": true,
        "reviewers": [
            {
                "type": "Team",
                "id": "development-team"
            }
        ],
        "deployment_branch_policy": null
    }'
    
    create_environment "approval-staging" "$staging_approval_rules"
    
    # Production approval environment
    local production_approval_rules='{
        "wait_timer": 0,
        "prevent_self_review": true,
        "reviewers": [
            {
                "type": "Team",
                "id": "platform-team"
            },
            {
                "type": "Team",
                "id": "security-team"
            }
        ],
        "deployment_branch_policy": null
    }'
    
    create_environment "approval-production" "$production_approval_rules"
}

# Setup environment secrets
setup_environment_secrets() {
    log_info "Setting up environment-specific secrets..."
    
    # Note: This is a placeholder - actual secret setup would require
    # the GitHub CLI or manual configuration through the GitHub UI
    log_warning "Environment secrets must be configured manually through GitHub UI:"
    log_warning "1. Go to Settings > Environments in your repository"
    log_warning "2. For each environment, add the required secrets:"
    log_warning "   - POSTGRES_PASSWORD"
    log_warning "   - REDIS_PASSWORD"
    log_warning "   - JWT_SECRET_KEY"
    log_warning "   - API keys (OPENAI_API_KEY, etc.)"
    log_warning "   - SSL certificates and keys"
    log_warning "   - Webhook secrets"
}

# Main execution
main() {
    log_info "Starting ACGS-1 GitHub Environments Setup"
    
    check_prerequisites
    
    setup_development_environment
    setup_staging_environment
    setup_production_environment
    setup_approval_environments
    setup_environment_secrets
    
    log_success "GitHub environments setup completed!"
    log_info "Next steps:"
    log_info "1. Configure environment secrets through GitHub UI"
    log_info "2. Set up team permissions for reviewers"
    log_info "3. Test the promotion gates workflow"
}

# Run main function
main "$@"
