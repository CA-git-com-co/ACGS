# ACGS Global Infrastructure Configuration
# Shared resources across all environments

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "acgs-terraform-state"
    key    = "global/terraform.tfstate"
    region = "us-east-1"
  }
}

# Provider Configuration
provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region for global resources"
  type        = string
  default     = "us-east-1"
}

variable "environment_prefix" {
  description = "Prefix for environment resources"
  type        = string
  default     = "acgs"
}

# S3 Bucket for Terraform State
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.environment_prefix}-terraform-state"
  
  tags = {
    Name        = "ACGS Terraform State"
    Environment = "global"
    Purpose     = "terraform-state"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# DynamoDB Table for Terraform State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name           = "${var.environment_prefix}-terraform-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "ACGS Terraform Locks"
    Environment = "global"
    Purpose     = "terraform-locking"
  }
}

# ECR Repository for ACGS Images
resource "aws_ecr_repository" "acgs_services" {
  for_each = toset([
    "auth-service",
    "ac-service", 
    "integrity-service",
    "fv-service",
    "gs-service",
    "pgc-service",
    "ec-service"
  ])

  name                 = "${var.environment_prefix}/${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "ACGS ${each.key}"
    Environment = "global"
    Service     = each.key
  }
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "acgs_services" {
  for_each = aws_ecr_repository.acgs_services

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 30
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# IAM Role for ACGS Services
resource "aws_iam_role" "acgs_service_role" {
  name = "${var.environment_prefix}-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "ACGS Service Role"
    Environment = "global"
  }
}

# IAM Policy for ACGS Services
resource "aws_iam_role_policy" "acgs_service_policy" {
  name = "${var.environment_prefix}-service-policy"
  role = aws_iam_role.acgs_service_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:*:*:secret:${var.environment_prefix}/*"
      }
    ]
  })
}

# Secrets Manager for ACGS Configuration
resource "aws_secretsmanager_secret" "acgs_config" {
  name        = "${var.environment_prefix}/global/config"
  description = "ACGS global configuration secrets"

  tags = {
    Name        = "ACGS Global Config"
    Environment = "global"
  }
}

resource "aws_secretsmanager_secret_version" "acgs_config" {
  secret_id = aws_secretsmanager_secret.acgs_config.id
  secret_string = jsonencode({
    constitutional_hash = "cdd01ef066bc6cf2"
    encryption_key     = "acgs-global-encryption-key"
    jwt_secret         = "acgs-jwt-secret-key"
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "acgs_services" {
  for_each = toset([
    "auth-service",
    "ac-service",
    "integrity-service", 
    "fv-service",
    "gs-service",
    "pgc-service",
    "ec-service"
  ])

  name              = "/aws/acgs/${each.key}"
  retention_in_days = 30

  tags = {
    Name        = "ACGS ${each.key} Logs"
    Environment = "global"
    Service     = each.key
  }
}

# Outputs
output "terraform_state_bucket" {
  description = "S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "terraform_locks_table" {
  description = "DynamoDB table for Terraform locks"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "ecr_repositories" {
  description = "ECR repositories for ACGS services"
  value = {
    for k, v in aws_ecr_repository.acgs_services : k => v.repository_url
  }
}

output "service_role_arn" {
  description = "IAM role ARN for ACGS services"
  value       = aws_iam_role.acgs_service_role.arn
}

output "secrets_manager_arn" {
  description = "Secrets Manager ARN for ACGS config"
  value       = aws_secretsmanager_secret.acgs_config.arn
}
