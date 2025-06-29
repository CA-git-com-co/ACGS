# ACGS Staging Environment Terraform Configuration

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "acgs-terraform-state"
    key    = "staging/terraform.tfstate"
    region = "us-east-1"
  }
}

# Local Variables
locals {
  environment = "staging"
  namespace   = "acgs-staging"
}

# ACGS Platform Module
module "acgs_platform" {
  source = "../../modules/acgs-platform"
  
  namespace         = local.namespace
  environment       = local.environment
  replica_count     = 1
  constitutional_hash = "cdd01ef066bc6cf2"
  
  resource_limits = {
    cpu    = "1000m"
    memory = "2Gi"
  }
  
  resource_requests = {
    cpu    = "250m"
    memory = "512Mi"
  }
}

# Monitoring Stack
module "monitoring" {
  source = "../../modules/monitoring"
  
  namespace   = "monitoring-staging"
  environment = local.environment
  
  prometheus_retention = "7d"
  prometheus_storage   = "20Gi"
  
  grafana_admin_password = "staging123"
  
  alert_manager_config = {
    smtp_smarthost = "localhost:587"
    smtp_from      = "staging-alerts@acgs.local"
  }
}

# Outputs
output "acgs_namespace" {
  value = module.acgs_platform.namespace
}

output "services" {
  value = module.acgs_platform.services
}
