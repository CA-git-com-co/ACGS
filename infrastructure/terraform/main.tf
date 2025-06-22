# ACGS-1 Lite Infrastructure as Code - Main Configuration
# Terraform configuration for ACGS-1 Lite Constitutional Governance System
# Implements the 3-service architecture with DGM sandbox safety patterns

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
  }

  backend "s3" {
    bucket         = "acgs-lite-terraform-state"
    key            = "acgs-lite/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "acgs-lite-terraform-locks"
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project             = "ACGS-1-Lite"
      System              = "Constitutional-Governance-Lite"
      Environment         = var.environment
      ConstitutionalHash  = var.constitutional_hash
      ManagedBy          = "Terraform"
      Owner              = "ACGS-Lite-Operations"
      CostCenter         = "Constitutional-Governance-Lite"
      Compliance         = "Required"
      Architecture       = "3-Service-DGM-Pattern"
    }
  }
}

# Configure Kubernetes Provider
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

# Configure Helm Provider
provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# Local values for common configurations
locals {
  name_prefix = "acgs-lite-${var.environment}"

  common_tags = {
    Project             = "ACGS-1-Lite"
    System              = "Constitutional-Governance-Lite"
    Environment         = var.environment
    ConstitutionalHash  = var.constitutional_hash
    ManagedBy          = "Terraform"
    Architecture       = "3-Service-DGM-Pattern"
  }

  # ACGS-1 Lite Core Services (3-service architecture)
  services = {
    policy_engine = {
      name = "policy-engine"
      port = 8001
      replicas = var.environment == "production" ? 3 : 2
      node_pool = "governance"
    }
    evolution_oversight = {
      name = "evolution-oversight"
      port = 8002
      replicas = var.environment == "production" ? 2 : 1
      node_pool = "governance"
    }
    audit_engine = {
      name = "audit-engine"
      port = 8003
      replicas = var.environment == "production" ? 2 : 1
      node_pool = "governance"
    }
    sandbox_controller = {
      name = "sandbox-controller"
      port = 8004
      replicas = var.environment == "production" ? 3 : 2
      node_pool = "workload"
    }
    human_review_dashboard = {
      name = "human-review-dashboard"
      port = 3000
      replicas = var.environment == "production" ? 2 : 1
      node_pool = "governance"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix         = local.name_prefix
  environment         = var.environment
  availability_zones  = slice(data.aws_availability_zones.available.names, 0, 3)
  vpc_cidr           = var.vpc_cidr
  
  tags = local.common_tags
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"
  
  name_prefix    = local.name_prefix
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  
  cluster_version = var.kubernetes_version
  
  node_groups = {
    # Governance Pool - Policy Engine, Evolution Oversight, Audit Engine
    governance = {
      instance_types = ["m5.2xlarge"] # 8 CPU, 32 GB RAM
      min_size      = 2
      max_size      = 3
      desired_size  = 2

      labels = {
        "node-pool" = "governance"
        "constitutional-compliance" = "required"
        "acgs-lite-role" = "governance"
      }

      taints = [
        {
          key    = "governance"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }

    # Monitoring Pool - Prometheus, Grafana, AlertManager
    monitoring = {
      instance_types = ["m5.xlarge"] # 4 CPU, 16 GB RAM
      min_size      = 2
      max_size      = 3
      desired_size  = 2

      labels = {
        "node-pool" = "monitoring"
        "acgs-lite-role" = "monitoring"
      }

      taints = [
        {
          key    = "monitoring"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }

    # Workload Pool - AI Agent Sandboxes
    workload = {
      instance_types = ["m5.4xlarge"] # 16 CPU, 64 GB RAM
      min_size      = 3
      max_size      = 5
      desired_size  = 3

      labels = {
        "node-pool" = "workload"
        "acgs-lite-role" = "workload"
        "sandbox-isolation" = "required"
      }

      taints = [
        {
          key    = "workload"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }
  
  tags = local.common_tags
}

# RDS Database Module
module "rds" {
  source = "./modules/rds"
  
  name_prefix    = local.name_prefix
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.database_subnet_ids
  
  instance_class = var.environment == "production" ? "db.r6g.xlarge" : "db.t3.medium"
  allocated_storage = var.environment == "production" ? 500 : 100
  
  database_name = "acgs_db"
  username      = "acgs_user"
  
  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  monitoring_enabled = var.environment == "production"
  
  tags = local.common_tags
}

# ElastiCache Redis Module
module "redis" {
  source = "./modules/redis"
  
  name_prefix    = local.name_prefix
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  
  node_type = var.environment == "production" ? "cache.r6g.large" : "cache.t3.micro"
  num_cache_nodes = var.environment == "production" ? 3 : 1
  
  tags = local.common_tags
}

# S3 Buckets Module
module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  buckets = {
    constitutional_documents = {
      versioning = true
      encryption = true
      lifecycle_rules = true
    }
    governance_artifacts = {
      versioning = true
      encryption = true
      lifecycle_rules = true
    }
    audit_logs = {
      versioning = true
      encryption = true
      lifecycle_rules = true
    }
    backups = {
      versioning = true
      encryption = true
      lifecycle_rules = true
    }
  }
  
  tags = local.common_tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  cluster_name = module.eks.cluster_name
  
  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security_groups"
  
  name_prefix = local.name_prefix
  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  
  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  cluster_name = module.eks.cluster_name
  
  tags = local.common_tags
}

# Kubernetes Namespaces for ACGS-1 Lite
resource "kubernetes_namespace" "acgs_lite_namespaces" {
  for_each = toset([
    "governance",    # Policy Engine, Evolution Oversight, Audit Engine
    "workload",      # AI Agent Sandboxes
    "monitoring",    # Prometheus, Grafana, AlertManager
    "shared"         # Shared resources and utilities
  ])

  metadata {
    name = each.value

    labels = {
      environment            = var.environment
      system                = "acgs-lite-constitutional-governance"
      constitutional-hash   = var.constitutional_hash
      managed-by           = "terraform"
      architecture         = "3-service-dgm-pattern"
    }

    annotations = {
      "description" = "ACGS-1 Lite Constitutional Governance System - ${each.value}"
      "acgs-lite.io/namespace-type" = each.value
    }
  }
}

# Kubernetes Secrets for ACGS-1 Lite
resource "kubernetes_secret" "acgs_lite_secrets" {
  for_each = toset(["governance", "workload", "shared"])

  metadata {
    name      = "acgs-lite-secrets"
    namespace = each.value
  }

  data = {
    database_url = "postgresql://${module.rds.username}:${module.rds.password}@${module.rds.endpoint}:5432/${module.rds.database_name}"
    redis_url    = "redis://${module.redis.endpoint}:6379/0"
    jwt_secret   = random_password.jwt_secret.result
    constitutional_hash = var.constitutional_hash
    redpanda_brokers = "constitutional-events-0.constitutional-events.governance.svc.cluster.local:9092,constitutional-events-1.constitutional-events.governance.svc.cluster.local:9092,constitutional-events-2.constitutional-events.governance.svc.cluster.local:9092"
    s3_audit_bucket = "acgs-lite-${var.environment}-audit-logs"
    opa_endpoint = "http://opa.governance.svc.cluster.local:8181"
  }

  type = "Opaque"
}

# Random password for JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Output important values
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.redis.endpoint
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "constitutional_hash" {
  description = "Constitutional hash for governance validation"
  value       = var.constitutional_hash
}
