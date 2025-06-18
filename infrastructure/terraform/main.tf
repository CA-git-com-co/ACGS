# ACGS-1 Infrastructure as Code - Main Configuration
# Terraform configuration for ACGS-1 Constitutional Governance System
# Supports multi-environment deployment with constitutional compliance

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
    bucket         = "acgs-terraform-state"
    key            = "acgs-1/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "acgs-terraform-locks"
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project             = "ACGS-1"
      System              = "Constitutional-Governance"
      Environment         = var.environment
      ConstitutionalHash  = var.constitutional_hash
      ManagedBy          = "Terraform"
      Owner              = "ACGS-Operations"
      CostCenter         = "Constitutional-Governance"
      Compliance         = "Required"
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
  name_prefix = "acgs-${var.environment}"
  
  common_tags = {
    Project             = "ACGS-1"
    System              = "Constitutional-Governance"
    Environment         = var.environment
    ConstitutionalHash  = var.constitutional_hash
    ManagedBy          = "Terraform"
  }
  
  # Service configuration
  services = {
    auth = {
      name = "auth-service"
      port = 8000
      replicas = var.environment == "production" ? 3 : 2
    }
    ac = {
      name = "ac-service"
      port = 8001
      replicas = var.environment == "production" ? 3 : 2
    }
    integrity = {
      name = "integrity-service"
      port = 8002
      replicas = var.environment == "production" ? 2 : 1
    }
    fv = {
      name = "fv-service"
      port = 8003
      replicas = var.environment == "production" ? 2 : 1
    }
    gs = {
      name = "gs-service"
      port = 8004
      replicas = var.environment == "production" ? 3 : 2
    }
    pgc = {
      name = "pgc-service"
      port = 8005
      replicas = var.environment == "production" ? 3 : 2
    }
    ec = {
      name = "ec-service"
      port = 8006
      replicas = var.environment == "production" ? 2 : 1
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
    system = {
      instance_types = ["t3.medium"]
      min_size      = 1
      max_size      = 3
      desired_size  = 2
      
      labels = {
        role = "system"
      }
      
      taints = []
    }
    
    acgs_services = {
      instance_types = ["t3.large"]
      min_size      = var.environment == "production" ? 3 : 2
      max_size      = var.environment == "production" ? 10 : 5
      desired_size  = var.environment == "production" ? 5 : 3
      
      labels = {
        role = "acgs-services"
      }
      
      taints = []
    }
    
    governance = {
      instance_types = ["t3.xlarge"]
      min_size      = var.environment == "production" ? 2 : 1
      max_size      = var.environment == "production" ? 5 : 3
      desired_size  = var.environment == "production" ? 3 : 2
      
      labels = {
        role = "governance"
        constitutional-compliance = "required"
      }
      
      taints = [
        {
          key    = "governance"
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

# Kubernetes Namespaces
resource "kubernetes_namespace" "acgs_namespaces" {
  for_each = toset(["acgs-blue", "acgs-green", "acgs-shared", "acgs-monitoring"])
  
  metadata {
    name = each.value
    
    labels = {
      environment            = var.environment
      system                = "acgs-constitutional-governance"
      constitutional-hash   = var.constitutional_hash
      managed-by           = "terraform"
    }
    
    annotations = {
      "description" = "ACGS-1 Constitutional Governance System - ${each.value}"
    }
  }
}

# Kubernetes Secrets
resource "kubernetes_secret" "acgs_secrets" {
  for_each = toset(["acgs-blue", "acgs-green"])
  
  metadata {
    name      = "acgs-secrets"
    namespace = each.value
  }
  
  data = {
    database_url = "postgresql://${module.rds.username}:${module.rds.password}@${module.rds.endpoint}:5432/${module.rds.database_name}"
    redis_url    = "redis://${module.redis.endpoint}:6379/0"
    jwt_secret   = random_password.jwt_secret.result
    constitutional_hash = var.constitutional_hash
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
