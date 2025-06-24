#!/bin/bash

# ACGS-1 Terraform Infrastructure Deployment Script
# Comprehensive infrastructure deployment for ACGS-1 Constitutional Governance System

set -euo pipefail

# Configuration
TERRAFORM_DIR="infrastructure/terraform"
ENVIRONMENTS=("development" "staging" "production")
AWS_REGION="${AWS_REGION:-us-west-2}"
CONSTITUTIONAL_HASH="${CONSTITUTIONAL_HASH:-cdd01ef066bc6cf2}"

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
ACGS-1 Terraform Infrastructure Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    init        Initialize Terraform backend and providers
    plan        Generate and show execution plan
    apply       Apply infrastructure changes
    destroy     Destroy infrastructure
    validate    Validate Terraform configuration
    format      Format Terraform files
    help        Show this help message

Options:
    --environment ENV       Target environment (development, staging, production)
    --region REGION         AWS region (default: us-west-2)
    --auto-approve         Auto-approve apply/destroy operations
    --var-file FILE        Additional variables file
    --target RESOURCE      Target specific resource
    --parallelism N        Limit concurrent operations

Examples:
    $0 init --environment development
    $0 plan --environment staging
    $0 apply --environment production --auto-approve
    $0 destroy --environment development --target module.vpc

Environment Variables:
    AWS_REGION             AWS region (default: us-west-2)
    CONSTITUTIONAL_HASH    Constitutional hash for governance validation
    TF_VAR_*              Terraform variables

EOF
}

# Parse command line arguments
parse_args() {
    COMMAND=""
    ENVIRONMENT=""
    AUTO_APPROVE=""
    VAR_FILE=""
    TARGET=""
    PARALLELISM=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            init|plan|apply|destroy|validate|format|help)
                COMMAND="$1"
                shift
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --region)
                AWS_REGION="$2"
                shift 2
                ;;
            --auto-approve)
                AUTO_APPROVE="-auto-approve"
                shift
                ;;
            --var-file)
                VAR_FILE="-var-file=$2"
                shift 2
                ;;
            --target)
                TARGET="-target=$2"
                shift 2
                ;;
            --parallelism)
                PARALLELISM="-parallelism=$2"
                shift 2
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

# Validate environment
validate_environment() {
    if [[ -n "$ENVIRONMENT" ]]; then
        if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
            log_error "Invalid environment: $ENVIRONMENT"
            log_info "Available environments: ${ENVIRONMENTS[*]}"
            exit 1
        fi
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Terraform is installed
    if ! command -v terraform >/dev/null 2>&1; then
        log_error "Terraform is not installed"
        exit 1
    fi
    
    # Check if AWS CLI is installed
    if ! command -v aws >/dev/null 2>&1; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Check if in correct directory
    if [[ ! -d "$TERRAFORM_DIR" ]]; then
        log_error "Terraform directory not found: $TERRAFORM_DIR"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Initialize Terraform
terraform_init() {
    log_info "Initializing Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize with backend configuration
    terraform init \
        -backend-config="bucket=acgs-terraform-state" \
        -backend-config="key=acgs-1/${ENVIRONMENT}/terraform.tfstate" \
        -backend-config="region=${AWS_REGION}" \
        -backend-config="encrypt=true" \
        -backend-config="dynamodb_table=acgs-terraform-locks"
    
    log_success "Terraform initialized successfully"
    cd - > /dev/null
}

# Validate Terraform configuration
terraform_validate() {
    log_info "Validating Terraform configuration..."
    
    cd "$TERRAFORM_DIR"
    terraform validate
    log_success "Terraform configuration is valid"
    cd - > /dev/null
}

# Format Terraform files
terraform_format() {
    log_info "Formatting Terraform files..."
    
    cd "$TERRAFORM_DIR"
    terraform fmt -recursive
    log_success "Terraform files formatted"
    cd - > /dev/null
}

# Generate Terraform plan
terraform_plan() {
    log_info "Generating Terraform plan for environment: $ENVIRONMENT"
    
    cd "$TERRAFORM_DIR"
    
    # Build terraform plan command
    local plan_cmd="terraform plan"
    plan_cmd="$plan_cmd -var=\"environment=$ENVIRONMENT\""
    plan_cmd="$plan_cmd -var=\"aws_region=$AWS_REGION\""
    plan_cmd="$plan_cmd -var=\"constitutional_hash=$CONSTITUTIONAL_HASH\""
    
    if [[ -n "$VAR_FILE" ]]; then
        plan_cmd="$plan_cmd $VAR_FILE"
    fi
    
    if [[ -n "$TARGET" ]]; then
        plan_cmd="$plan_cmd $TARGET"
    fi
    
    plan_cmd="$plan_cmd -out=tfplan-$ENVIRONMENT"
    
    # Execute plan
    eval "$plan_cmd"
    
    log_success "Terraform plan generated: tfplan-$ENVIRONMENT"
    cd - > /dev/null
}

# Apply Terraform changes
terraform_apply() {
    log_info "Applying Terraform changes for environment: $ENVIRONMENT"
    
    cd "$TERRAFORM_DIR"
    
    # Check if plan file exists
    if [[ -f "tfplan-$ENVIRONMENT" ]]; then
        log_info "Using existing plan file: tfplan-$ENVIRONMENT"
        terraform apply $AUTO_APPROVE "tfplan-$ENVIRONMENT"
    else
        log_info "No plan file found, generating and applying..."
        
        # Build terraform apply command
        local apply_cmd="terraform apply"
        apply_cmd="$apply_cmd -var=\"environment=$ENVIRONMENT\""
        apply_cmd="$apply_cmd -var=\"aws_region=$AWS_REGION\""
        apply_cmd="$apply_cmd -var=\"constitutional_hash=$CONSTITUTIONAL_HASH\""
        
        if [[ -n "$VAR_FILE" ]]; then
            apply_cmd="$apply_cmd $VAR_FILE"
        fi
        
        if [[ -n "$TARGET" ]]; then
            apply_cmd="$apply_cmd $TARGET"
        fi
        
        if [[ -n "$PARALLELISM" ]]; then
            apply_cmd="$apply_cmd $PARALLELISM"
        fi
        
        apply_cmd="$apply_cmd $AUTO_APPROVE"
        
        # Execute apply
        eval "$apply_cmd"
    fi
    
    log_success "Terraform changes applied successfully"
    cd - > /dev/null
}

# Destroy Terraform infrastructure
terraform_destroy() {
    log_warning "Destroying Terraform infrastructure for environment: $ENVIRONMENT"
    
    if [[ "$ENVIRONMENT" == "production" && -z "$AUTO_APPROVE" ]]; then
        log_warning "You are about to destroy PRODUCTION infrastructure!"
        read -p "Are you absolutely sure? Type 'yes' to continue: " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Destroy operation cancelled"
            exit 0
        fi
    fi
    
    cd "$TERRAFORM_DIR"
    
    # Build terraform destroy command
    local destroy_cmd="terraform destroy"
    destroy_cmd="$destroy_cmd -var=\"environment=$ENVIRONMENT\""
    destroy_cmd="$destroy_cmd -var=\"aws_region=$AWS_REGION\""
    destroy_cmd="$destroy_cmd -var=\"constitutional_hash=$CONSTITUTIONAL_HASH\""
    
    if [[ -n "$VAR_FILE" ]]; then
        destroy_cmd="$destroy_cmd $VAR_FILE"
    fi
    
    if [[ -n "$TARGET" ]]; then
        destroy_cmd="$destroy_cmd $TARGET"
    fi
    
    if [[ -n "$PARALLELISM" ]]; then
        destroy_cmd="$destroy_cmd $PARALLELISM"
    fi
    
    destroy_cmd="$destroy_cmd $AUTO_APPROVE"
    
    # Execute destroy
    eval "$destroy_cmd"
    
    log_success "Terraform infrastructure destroyed"
    cd - > /dev/null
}

# Create backend resources if they don't exist
create_backend_resources() {
    log_info "Creating Terraform backend resources..."
    
    # Create S3 bucket for state
    if ! aws s3 ls "s3://acgs-terraform-state" >/dev/null 2>&1; then
        log_info "Creating S3 bucket for Terraform state..."
        aws s3 mb "s3://acgs-terraform-state" --region "$AWS_REGION"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "acgs-terraform-state" \
            --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket "acgs-terraform-state" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
    fi
    
    # Create DynamoDB table for locking
    if ! aws dynamodb describe-table --table-name "acgs-terraform-locks" >/dev/null 2>&1; then
        log_info "Creating DynamoDB table for Terraform locks..."
        aws dynamodb create-table \
            --table-name "acgs-terraform-locks" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
            --region "$AWS_REGION"
        
        # Wait for table to be active
        aws dynamodb wait table-exists --table-name "acgs-terraform-locks" --region "$AWS_REGION"
    fi
    
    log_success "Backend resources ready"
}

# Main execution
main() {
    log_info "ACGS-1 Terraform Infrastructure Deployment"
    log_info "Environment: ${ENVIRONMENT:-'not specified'}"
    log_info "Region: $AWS_REGION"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    check_prerequisites
    
    # Create backend resources if needed
    if [[ "$COMMAND" == "init" ]]; then
        create_backend_resources
    fi
    
    case "$COMMAND" in
        "init")
            terraform_init
            ;;
        "validate")
            terraform_validate
            ;;
        "format")
            terraform_format
            ;;
        "plan")
            if [[ -z "$ENVIRONMENT" ]]; then
                log_error "Environment is required for plan command"
                exit 1
            fi
            terraform_init
            terraform_validate
            terraform_plan
            ;;
        "apply")
            if [[ -z "$ENVIRONMENT" ]]; then
                log_error "Environment is required for apply command"
                exit 1
            fi
            terraform_init
            terraform_validate
            terraform_apply
            ;;
        "destroy")
            if [[ -z "$ENVIRONMENT" ]]; then
                log_error "Environment is required for destroy command"
                exit 1
            fi
            terraform_init
            terraform_destroy
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
validate_environment
main
