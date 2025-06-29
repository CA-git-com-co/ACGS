# ACGS Terraform Version Constraints
# Defines version constraints for Terraform and providers

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2"
    }
    
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
  
  # Backend configuration for state management
  backend "s3" {
    # Backend configuration is provided via backend config files
    # or environment variables for different environments
  }
}

# Provider version constraints and features
provider "aws" {
  # AWS provider configuration
  region = var.aws_region
  
  # Default tags applied to all resources
  default_tags {
    tags = {
      Project             = "ACGS"
      ManagedBy          = "Terraform"
      Environment        = var.environment
      TerraformVersion   = "~> 1.0"
      AWSProviderVersion = "~> 5.0"
      CreatedDate        = formatdate("YYYY-MM-DD", timestamp())
    }
  }
  
  # Assume role configuration (if needed)
  dynamic "assume_role" {
    for_each = var.assume_role_arn != "" ? [1] : []
    content {
      role_arn     = var.assume_role_arn
      session_name = "terraform-acgs-${var.environment}"
      external_id  = var.external_id
    }
  }
}

# Kubernetes provider version constraints
provider "kubernetes" {
  # Configuration is handled in providers.tf
  experiments {
    manifest_resource = true
  }
}

# Helm provider version constraints
provider "helm" {
  # Configuration is handled in providers.tf
  experiments {
    manifest = true
  }
}

# Variables for version configuration
variable "assume_role_arn" {
  description = "ARN of the role to assume for AWS operations"
  type        = string
  default     = ""
}

variable "external_id" {
  description = "External ID for assume role"
  type        = string
  default     = ""
}

# Version information outputs
output "terraform_version" {
  description = "Terraform version used"
  value       = "~> 1.0"
}

output "provider_versions" {
  description = "Provider versions used"
  value = {
    aws        = "~> 5.0"
    kubernetes = "~> 2.23"
    helm       = "~> 2.11"
    random     = "~> 3.5"
    tls        = "~> 4.0"
    local      = "~> 2.4"
    null       = "~> 3.2"
    template   = "~> 2.2"
    archive    = "~> 2.4"
    time       = "~> 0.9"
  }
}

# Feature flags for experimental features
locals {
  experimental_features = {
    kubernetes_manifest_resource = true
    helm_manifest              = true
    aws_s3_bucket_v2          = true
    aws_instance_metadata_v2  = true
  }
}

# Terraform configuration validation
check "terraform_version" {
  assert {
    condition     = can(regex("^1\\.", terraform.version))
    error_message = "Terraform version must be 1.x"
  }
}

check "aws_provider_version" {
  assert {
    condition     = can(regex("^5\\.", provider::aws.version))
    error_message = "AWS provider version must be 5.x"
  }
}

# Minimum required versions for security and stability
locals {
  minimum_versions = {
    terraform  = "1.0.0"
    aws        = "5.0.0"
    kubernetes = "2.23.0"
    helm       = "2.11.0"
  }
}

# Version compatibility matrix
locals {
  compatibility_matrix = {
    terraform_1_0 = {
      aws_5_0        = true
      kubernetes_2_23 = true
      helm_2_11      = true
    }
    terraform_1_5 = {
      aws_5_0        = true
      kubernetes_2_23 = true
      helm_2_11      = true
    }
  }
}
