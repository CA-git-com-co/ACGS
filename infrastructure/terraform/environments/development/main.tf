# ACGS Development Environment Terraform Configuration

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

# Local Variables
locals {
  environment = "development"
  namespace   = "acgs-dev"
}

# ACGS Platform Module
module "acgs_platform" {
  source = "../../modules/acgs-platform"
  
  namespace         = local.namespace
  environment       = local.environment
  replica_count     = 1
  constitutional_hash = "cdd01ef066bc6cf2"
  
  resource_limits = {
    cpu    = "500m"
    memory = "1Gi"
  }
  
  resource_requests = {
    cpu    = "100m"
    memory = "256Mi"
  }
}

# Outputs
output "acgs_namespace" {
  value = module.acgs_platform.namespace
}

output "services" {
  value = module.acgs_platform.services
}
