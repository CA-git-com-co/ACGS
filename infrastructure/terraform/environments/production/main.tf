# ACGS Production Environment Terraform Configuration
# Enterprise-grade production infrastructure

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
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  backend "s3" {
    bucket = "acgs-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

# Provider Configuration
provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

# Local Variables
locals {
  environment = "production"
  namespace   = "acgs-production"
  
  common_labels = {
    environment = local.environment
    managed-by  = "terraform"
    platform    = "acgs"
  }
}

# ACGS Platform Module
module "acgs_platform" {
  source = "../../modules/acgs-platform"
  
  namespace         = local.namespace
  environment       = local.environment
  replica_count     = 3
  constitutional_hash = "cdd01ef066bc6cf2"
  
  resource_limits = {
    cpu    = "2000m"
    memory = "4Gi"
  }
  
  resource_requests = {
    cpu    = "500m"
    memory = "1Gi"
  }
}

# Monitoring Stack
module "monitoring" {
  source = "../../modules/monitoring"
  
  namespace   = "monitoring"
  environment = local.environment
  
  prometheus_retention = "30d"
  prometheus_storage   = "100Gi"
  
  grafana_admin_password = var.grafana_admin_password
  
  alert_manager_config = {
    smtp_smarthost = var.smtp_smarthost
    smtp_from      = var.smtp_from
  }
}

# Security Stack
module "security" {
  source = "../../modules/security"
  
  namespace   = local.namespace
  environment = local.environment
  
  enable_network_policies = true
  enable_pod_security     = true
  enable_rbac            = true
}

# Backup and Disaster Recovery
module "backup" {
  source = "../../modules/backup"
  
  namespace   = local.namespace
  environment = local.environment
  
  backup_schedule     = "0 */6 * * *"
  backup_retention    = "30d"
  backup_storage_size = "500Gi"
}

# Outputs
output "acgs_namespace" {
  description = "ACGS production namespace"
  value       = module.acgs_platform.namespace
}

output "acgs_services" {
  description = "ACGS services endpoints"
  value       = module.acgs_platform.services
}

output "monitoring_endpoints" {
  description = "Monitoring stack endpoints"
  value       = module.monitoring.endpoints
}

output "constitutional_hash" {
  description = "Constitutional compliance hash"
  value       = module.acgs_platform.constitutional_hash
}
