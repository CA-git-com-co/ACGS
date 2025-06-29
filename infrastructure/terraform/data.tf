# ACGS Terraform Data Sources
# Centralized data sources for ACGS infrastructure

# Current AWS caller identity
data "aws_caller_identity" "current" {}

# Current AWS region
data "aws_region" "current" {}

# Available AWS availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Latest EKS optimized AMI
data "aws_ami" "eks_worker" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amazon-eks-node-${var.kubernetes_version}-v*"]
  }
}

# EKS cluster OIDC issuer URL
data "aws_eks_cluster" "main" {
  count = var.create_eks_cluster ? 1 : 0
  name  = local.cluster_name
}

# TLS certificate for EKS OIDC
data "tls_certificate" "eks_oidc" {
  count = var.create_eks_cluster ? 1 : 0
  url   = data.aws_eks_cluster.main[0].identity[0].oidc[0].issuer
}

# IAM policy document for EKS cluster service role
data "aws_iam_policy_document" "eks_cluster_assume_role" {
  statement {
    effect = "Allow"
    
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
    
    actions = ["sts:AssumeRole"]
  }
}

# IAM policy document for EKS node group role
data "aws_iam_policy_document" "eks_node_assume_role" {
  statement {
    effect = "Allow"
    
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    
    actions = ["sts:AssumeRole"]
  }
}

# IAM policy document for ACGS services
data "aws_iam_policy_document" "acgs_service_policy" {
  statement {
    effect = "Allow"
    
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    
    resources = [
      "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:acgs/*"
    ]
  }
  
  statement {
    effect = "Allow"
    
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    
    resources = [
      "arn:aws:s3:::${local.name_prefix}-*/*"
    ]
  }
  
  statement {
    effect = "Allow"
    
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams"
    ]
    
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/acgs/*"
    ]
  }
  
  statement {
    effect = "Allow"
    
    actions = [
      "cloudwatch:PutMetricData",
      "cloudwatch:GetMetricStatistics",
      "cloudwatch:ListMetrics"
    ]
    
    resources = ["*"]
    
    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values   = ["ACGS/Application", "ACGS/Infrastructure"]
    }
  }
}

# Route53 hosted zone (if exists)
data "aws_route53_zone" "main" {
  count        = var.domain_name != "" ? 1 : 0
  name         = var.domain_name
  private_zone = false
}

# ACM certificate (if domain is provided)
data "aws_acm_certificate" "main" {
  count    = var.domain_name != "" ? 1 : 0
  domain   = var.domain_name
  statuses = ["ISSUED"]
}

# KMS key for encryption
data "aws_kms_key" "ebs" {
  key_id = "alias/aws/ebs"
}

data "aws_kms_key" "s3" {
  key_id = "alias/aws/s3"
}

# VPC endpoints for private connectivity
data "aws_vpc_endpoint_service" "s3" {
  service = "s3"
}

data "aws_vpc_endpoint_service" "dynamodb" {
  service = "dynamodb"
}

data "aws_vpc_endpoint_service" "ecr_api" {
  service = "ecr.api"
}

data "aws_vpc_endpoint_service" "ecr_dkr" {
  service = "ecr.dkr"
}

# Security group rules for common services
data "aws_security_group" "default" {
  count  = var.use_default_vpc ? 1 : 0
  vpc_id = data.aws_vpc.default[0].id
  name   = "default"
}

data "aws_vpc" "default" {
  count   = var.use_default_vpc ? 1 : 0
  default = true
}

data "aws_subnets" "default" {
  count = var.use_default_vpc ? 1 : 0
  
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default[0].id]
  }
}

# Variables for data sources
variable "kubernetes_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.24"
}

variable "create_eks_cluster" {
  description = "Whether to create EKS cluster"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for ACGS platform"
  type        = string
  default     = ""
}

variable "use_default_vpc" {
  description = "Whether to use default VPC"
  type        = bool
  default     = false
}

# Local values derived from data sources
locals {
  cluster_name = "${local.name_prefix}-cluster"
  account_id   = data.aws_caller_identity.current.account_id
  region       = data.aws_region.current.name
  
  # Availability zones (limit to 3 for cost optimization)
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
  
  # OIDC provider URL (if EKS cluster exists)
  oidc_provider_url = var.create_eks_cluster ? replace(data.aws_eks_cluster.main[0].identity[0].oidc[0].issuer, "https://", "") : ""
}
