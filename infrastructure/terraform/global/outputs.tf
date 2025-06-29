# ACGS Global Infrastructure Outputs

output "terraform_state_bucket" {
  description = "S3 bucket for Terraform state storage"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "terraform_state_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.arn
}

output "terraform_locks_table" {
  description = "DynamoDB table for Terraform state locking"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "terraform_locks_table_arn" {
  description = "ARN of the DynamoDB table for Terraform locks"
  value       = aws_dynamodb_table.terraform_locks.arn
}

output "ecr_repositories" {
  description = "ECR repositories for ACGS services"
  value = {
    for k, v in aws_ecr_repository.acgs_services : k => {
      name           = v.name
      repository_url = v.repository_url
      registry_id    = v.registry_id
      arn           = v.arn
    }
  }
}

output "ecr_repository_urls" {
  description = "ECR repository URLs for ACGS services"
  value = {
    for k, v in aws_ecr_repository.acgs_services : k => v.repository_url
  }
}

output "service_role_arn" {
  description = "IAM role ARN for ACGS services"
  value       = aws_iam_role.acgs_service_role.arn
}

output "service_role_name" {
  description = "IAM role name for ACGS services"
  value       = aws_iam_role.acgs_service_role.name
}

output "secrets_manager_arn" {
  description = "Secrets Manager ARN for ACGS global configuration"
  value       = aws_secretsmanager_secret.acgs_config.arn
}

output "secrets_manager_name" {
  description = "Secrets Manager name for ACGS global configuration"
  value       = aws_secretsmanager_secret.acgs_config.name
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups for ACGS services"
  value = {
    for k, v in aws_cloudwatch_log_group.acgs_services : k => {
      name              = v.name
      arn              = v.arn
      retention_in_days = v.retention_in_days
    }
  }
}

output "cloudwatch_log_group_names" {
  description = "CloudWatch log group names for ACGS services"
  value = {
    for k, v in aws_cloudwatch_log_group.acgs_services : k => v.name
  }
}

output "aws_region" {
  description = "AWS region where global resources are deployed"
  value       = var.aws_region
}

output "environment_prefix" {
  description = "Environment prefix used for resource naming"
  value       = var.environment_prefix
}

output "constitutional_hash" {
  description = "Constitutional compliance hash (sensitive)"
  value       = var.constitutional_hash
  sensitive   = true
}

output "common_tags" {
  description = "Common tags applied to all resources"
  value       = var.common_tags
}

output "resource_summary" {
  description = "Summary of created global resources"
  value = {
    s3_buckets = {
      terraform_state = aws_s3_bucket.terraform_state.bucket
    }
    dynamodb_tables = {
      terraform_locks = aws_dynamodb_table.terraform_locks.name
    }
    ecr_repositories = length(aws_ecr_repository.acgs_services)
    iam_roles = {
      service_role = aws_iam_role.acgs_service_role.name
    }
    secrets_manager = {
      global_config = aws_secretsmanager_secret.acgs_config.name
    }
    cloudwatch_log_groups = length(aws_cloudwatch_log_group.acgs_services)
  }
}

output "operational_excellence_config" {
  description = "Configuration for operational excellence monitoring"
  value = {
    monitoring_enabled     = var.enable_monitoring
    backup_enabled        = var.enable_backup
    security_scanning     = var.enable_security_scanning
    disaster_recovery     = var.enable_disaster_recovery
    compliance_monitoring = var.enable_compliance_monitoring
    rto_target_minutes   = var.rto_target_minutes
    rpo_target_minutes   = var.rpo_target_minutes
    log_retention_days   = var.log_retention_days
  }
}

output "security_configuration" {
  description = "Security configuration summary"
  value = {
    encryption_enabled           = var.enable_encryption
    vulnerability_scanning       = var.enable_vulnerability_scanning
    security_notification_email = var.security_notification_email
    compliance_frameworks       = var.compliance_frameworks
  }
}

output "performance_configuration" {
  description = "Performance monitoring configuration"
  value = {
    monitoring_enabled    = var.enable_performance_monitoring
    cpu_threshold        = var.performance_threshold_cpu
    memory_threshold     = var.performance_threshold_memory
    cost_optimization    = var.enable_cost_optimization
  }
}

output "backup_configuration" {
  description = "Backup and disaster recovery configuration"
  value = {
    backup_enabled           = var.enable_backup
    retention_days          = var.backup_retention_days
    cross_region_backup     = var.enable_cross_region_backup
    backup_regions          = var.backup_regions
    disaster_recovery       = var.enable_disaster_recovery
  }
}

output "infrastructure_endpoints" {
  description = "Key infrastructure endpoints and identifiers"
  value = {
    terraform_backend = {
      bucket         = aws_s3_bucket.terraform_state.bucket
      dynamodb_table = aws_dynamodb_table.terraform_locks.name
      region         = var.aws_region
    }
    container_registry = {
      for k, v in aws_ecr_repository.acgs_services : k => v.repository_url
    }
    secrets_manager = aws_secretsmanager_secret.acgs_config.arn
    service_role    = aws_iam_role.acgs_service_role.arn
  }
}
