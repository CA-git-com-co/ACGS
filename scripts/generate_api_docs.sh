#!/bin/bash
set -e

# ACGS-1 API Documentation Generation Script
# 
# This script automates the generation of OpenAPI documentation for all ACGS services
# and integrates with CI/CD pipelines for continuous documentation updates.
#
# Usage:
#   ./scripts/generate_api_docs.sh [options]
#
# Options:
#   --services <list>     Comma-separated list of services (default: all)
#   --output <dir>        Output directory (default: docs/api/generated)
#   --format <formats>    Output formats: json,yaml,html (default: all)
#   --mock               Use mock FastAPI apps instead of real discovery
#   --combined           Generate combined specification
#   --deploy             Deploy to documentation site
#   --validate           Validate documentation synchronization
#   --baseline           Update documentation baseline
#   --verbose            Enable verbose logging
#   --help               Show this help message

# Default configuration
SERVICES="all"
OUTPUT_DIR="docs/api/generated"
FORMATS="json,yaml,html"
USE_MOCK=false
GENERATE_COMBINED=true
DEPLOY=false
VALIDATE=false
UPDATE_BASELINE=false
VERBOSE=false

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
ACGS-1 API Documentation Generation Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --services <list>     Comma-separated list of services to generate docs for
                         Available: auth,ac,integrity,fv,gs,pgc,ec,dgm,all
                         Default: all

    --output <dir>        Output directory for generated documentation
                         Default: docs/api/generated

    --format <formats>    Output formats (comma-separated)
                         Available: json,yaml,html
                         Default: json,yaml,html

    --mock               Use mock FastAPI applications instead of service discovery
                         Useful when services are not running

    --combined           Generate combined specification for all services
                         Default: enabled

    --deploy             Deploy documentation to GitHub Pages or documentation site
                         Requires appropriate permissions

    --validate           Validate documentation synchronization with code
                         Exits with error if documentation is out of sync

    --baseline           Update documentation baseline for change detection
                         Use after confirming API changes are intentional

    --verbose            Enable verbose logging and debug output

    --help               Show this help message

EXAMPLES:
    # Generate documentation for all services
    $0

    # Generate docs for specific services only
    $0 --services auth,ac,integrity

    # Generate and deploy documentation
    $0 --deploy

    # Validate documentation synchronization
    $0 --validate

    # Update baseline after API changes
    $0 --baseline

    # Generate with verbose output
    $0 --verbose --mock

ENVIRONMENT VARIABLES:
    DOCS_OUTPUT_DIR      Override default output directory
    DOCS_DEPLOY_URL      Documentation deployment URL
    GITHUB_TOKEN         GitHub token for deployment (if using GitHub Pages)

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --services)
            SERVICES="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --format)
            FORMATS="$2"
            shift 2
            ;;
        --mock)
            USE_MOCK=true
            shift
            ;;
        --combined)
            GENERATE_COMBINED=true
            shift
            ;;
        --deploy)
            DEPLOY=true
            shift
            ;;
        --validate)
            VALIDATE=true
            shift
            ;;
        --baseline)
            UPDATE_BASELINE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Override with environment variables if set
OUTPUT_DIR="${DOCS_OUTPUT_DIR:-$OUTPUT_DIR}"

# Validate dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check required Python packages
    python3 -c "import yaml, json" 2>/dev/null || {
        log_error "Required Python packages not installed. Run: pip install pyyaml"
        exit 1
    }
    
    # Check if documentation generator exists
    if [[ ! -f "tools/documentation/openapi_generator.py" ]]; then
        log_error "OpenAPI generator not found at tools/documentation/openapi_generator.py"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Setup output directory
setup_output_dir() {
    log_info "Setting up output directory: $OUTPUT_DIR"
    
    mkdir -p "$OUTPUT_DIR"
    
    # Create .gitignore if it doesn't exist
    if [[ ! -f "$OUTPUT_DIR/.gitignore" ]]; then
        cat > "$OUTPUT_DIR/.gitignore" << EOF
# Generated API documentation
*.json
*.yaml
*.html

# Keep directory structure
!.gitignore
!README.md
EOF
    fi
    
    # Create README if it doesn't exist
    if [[ ! -f "$OUTPUT_DIR/README.md" ]]; then
        cat > "$OUTPUT_DIR/README.md" << EOF
# Generated API Documentation

This directory contains automatically generated OpenAPI documentation for ACGS services.

## Files

- \`*_openapi.json\` - OpenAPI 3.0 specifications in JSON format
- \`*_openapi.yaml\` - OpenAPI 3.0 specifications in YAML format  
- \`*_docs.html\` - Interactive Swagger UI documentation
- \`combined_*\` - Combined documentation for all services
- \`index.html\` - Documentation portal homepage

## Generation

Documentation is automatically generated from FastAPI applications using:

\`\`\`bash
./scripts/generate_api_docs.sh
\`\`\`

Last generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
    fi
    
    log_success "Output directory setup complete"
}

# Generate documentation
generate_documentation() {
    log_info "Generating API documentation..."
    
    # Build generator command
    local cmd="python3 tools/documentation/openapi_generator.py"
    
    if [[ "$SERVICES" != "all" ]]; then
        cmd="$cmd --service $SERVICES"
    else
        cmd="$cmd --service all"
    fi
    
    cmd="$cmd --output $OUTPUT_DIR"
    cmd="$cmd --format $(echo $FORMATS | tr ',' ' ')"
    
    if [[ "$USE_MOCK" == "true" ]]; then
        cmd="$cmd --mock"
    fi
    
    if [[ "$GENERATE_COMBINED" == "true" ]]; then
        cmd="$cmd --combined"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi
    
    log_info "Running: $cmd"
    
    # Execute documentation generation
    if eval "$cmd"; then
        log_success "Documentation generation completed"
    else
        log_error "Documentation generation failed"
        exit 1
    fi
}

# Validate documentation
validate_documentation() {
    if [[ "$VALIDATE" != "true" ]]; then
        return 0
    fi
    
    log_info "Validating documentation synchronization..."
    
    local cmd="python3 tools/documentation/doc_sync.py --action validate"
    cmd="$cmd --docs-dir $OUTPUT_DIR"
    
    if [[ "$SERVICES" != "all" ]]; then
        cmd="$cmd --services $(echo $SERVICES | tr ',' ' ')"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi
    
    # Generate validation report
    local report_file="$OUTPUT_DIR/sync_report.md"
    cmd="$cmd --output $report_file"
    
    log_info "Running: $cmd"
    
    if eval "$cmd"; then
        log_success "Documentation validation passed"
        if [[ -f "$report_file" ]]; then
            log_info "Validation report saved to: $report_file"
        fi
    else
        log_error "Documentation validation failed - documentation is out of sync"
        if [[ -f "$report_file" ]]; then
            log_info "Check validation report: $report_file"
        fi
        exit 1
    fi
}

# Update baseline
update_baseline() {
    if [[ "$UPDATE_BASELINE" != "true" ]]; then
        return 0
    fi
    
    log_info "Updating documentation baseline..."
    
    local cmd="python3 tools/documentation/doc_sync.py --action baseline"
    cmd="$cmd --docs-dir $OUTPUT_DIR"
    
    if [[ "$SERVICES" != "all" ]]; then
        cmd="$cmd --services $(echo $SERVICES | tr ',' ' ')"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi
    
    log_info "Running: $cmd"
    
    if eval "$cmd"; then
        log_success "Documentation baseline updated"
    else
        log_error "Failed to update documentation baseline"
        exit 1
    fi
}

# Deploy documentation
deploy_documentation() {
    if [[ "$DEPLOY" != "true" ]]; then
        return 0
    fi
    
    log_info "Deploying documentation..."
    
    # Check if we're in a CI environment
    if [[ -n "$GITHUB_ACTIONS" ]]; then
        log_info "Detected GitHub Actions environment"
        # Deployment will be handled by GitHub Actions workflow
        log_success "Documentation prepared for GitHub Actions deployment"
        return 0
    fi
    
    # Check for GitHub Pages deployment
    if [[ -n "$GITHUB_TOKEN" ]] && command -v gh &> /dev/null; then
        log_info "Deploying to GitHub Pages..."
        
        # Use GitHub CLI to deploy
        gh workflow run api-documentation.yml --field deploy=true
        
        log_success "GitHub Pages deployment triggered"
    else
        log_warning "No deployment method configured"
        log_info "To deploy documentation:"
        log_info "  1. Set GITHUB_TOKEN environment variable"
        log_info "  2. Install GitHub CLI (gh)"
        log_info "  3. Or configure your preferred deployment method"
    fi
}

# Generate summary report
generate_summary() {
    log_info "Generating documentation summary..."
    
    local summary_file="$OUTPUT_DIR/generation_summary.json"
    
    # Count generated files
    local json_files=$(find "$OUTPUT_DIR" -name "*.json" | wc -l)
    local yaml_files=$(find "$OUTPUT_DIR" -name "*.yaml" | wc -l)
    local html_files=$(find "$OUTPUT_DIR" -name "*.html" | wc -l)
    
    # Create summary JSON
    cat > "$summary_file" << EOF
{
  "generation_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "services_requested": "$SERVICES",
  "output_directory": "$OUTPUT_DIR",
  "formats_generated": "$FORMATS",
  "use_mock": $USE_MOCK,
  "combined_spec": $GENERATE_COMBINED,
  "files_generated": {
    "json": $json_files,
    "yaml": $yaml_files,
    "html": $html_files,
    "total": $((json_files + yaml_files + html_files))
  },
  "validation_performed": $VALIDATE,
  "baseline_updated": $UPDATE_BASELINE,
  "deployment_requested": $DEPLOY
}
EOF
    
    log_success "Documentation generation summary:"
    log_info "  Services: $SERVICES"
    log_info "  Output: $OUTPUT_DIR"
    log_info "  Files generated: $((json_files + yaml_files + html_files))"
    log_info "  Summary saved to: $summary_file"
}

# Main execution
main() {
    log_info "Starting ACGS API documentation generation"
    log_info "Services: $SERVICES"
    log_info "Output: $OUTPUT_DIR"
    log_info "Formats: $FORMATS"
    
    # Execute steps
    check_dependencies
    setup_output_dir
    
    # Update baseline first if requested
    update_baseline
    
    # Generate documentation
    generate_documentation
    
    # Validate if requested
    validate_documentation
    
    # Deploy if requested
    deploy_documentation
    
    # Generate summary
    generate_summary
    
    log_success "API documentation generation completed successfully!"
    
    if [[ "$DEPLOY" == "true" ]]; then
        log_info "Documentation deployment initiated"
    else
        log_info "To view documentation, open: $OUTPUT_DIR/index.html"
    fi
}

# Execute main function
main "$@"
