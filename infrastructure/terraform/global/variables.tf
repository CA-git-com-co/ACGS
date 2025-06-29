# ACGS Global Infrastructure Variables

variable "aws_region" {
  description = "AWS region for global resources"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition = contains([
      "us-east-1", "us-east-2", "us-west-1", "us-west-2",
      "eu-west-1", "eu-west-2", "eu-central-1",
      "ap-southeast-1", "ap-southeast-2", "ap-northeast-1"
    ], var.aws_region)
    error_message = "AWS region must be a valid region."
  }
}

variable "environment_prefix" {
  description = "Prefix for environment resources"
  type        = string
  default     = "acgs"
  
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.environment_prefix))
    error_message = "Environment prefix must start with a letter, contain only lowercase letters, numbers, and hyphens, and end with a letter or number."
  }
}

variable "enable_versioning" {
  description = "Enable versioning for S3 buckets"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Enable encryption for resources"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

variable "ecr_image_count_limit" {
  description = "Maximum number of images to keep in ECR repositories"
  type        = number
  default     = 30
  
  validation {
    condition     = var.ecr_image_count_limit > 0 && var.ecr_image_count_limit <= 1000
    error_message = "ECR image count limit must be between 1 and 1000."
  }
}

variable "constitutional_hash" {
  description = "Constitutional compliance hash"
  type        = string
  default     = "cdd01ef066bc6cf2"
  sensitive   = true
  
  validation {
    condition     = can(regex("^[a-f0-9]{16}$", var.constitutional_hash))
    error_message = "Constitutional hash must be a 16-character hexadecimal string."
  }
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "ACGS"
    ManagedBy   = "Terraform"
    Environment = "global"
    Owner       = "ACGS-Team"
  }
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable backup for resources"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention days must be between 1 and 365."
  }
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup replication"
  type        = bool
  default     = false
}

variable "backup_regions" {
  description = "List of regions for backup replication"
  type        = list(string)
  default     = ["us-west-2"]
  
  validation {
    condition = alltrue([
      for region in var.backup_regions : contains([
        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
        "eu-west-1", "eu-west-2", "eu-central-1",
        "ap-southeast-1", "ap-southeast-2", "ap-northeast-1"
      ], region)
    ])
    error_message = "All backup regions must be valid AWS regions."
  }
}

variable "enable_security_scanning" {
  description = "Enable security scanning for ECR repositories"
  type        = bool
  default     = true
}

variable "enable_vulnerability_scanning" {
  description = "Enable vulnerability scanning"
  type        = bool
  default     = true
}

variable "security_notification_email" {
  description = "Email address for security notifications"
  type        = string
  default     = "security@acgs.local"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.security_notification_email))
    error_message = "Security notification email must be a valid email address."
  }
}

variable "enable_cost_optimization" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "enable_performance_monitoring" {
  description = "Enable performance monitoring"
  type        = bool
  default     = true
}

variable "performance_threshold_cpu" {
  description = "CPU utilization threshold for alerts (percentage)"
  type        = number
  default     = 80
  
  validation {
    condition     = var.performance_threshold_cpu > 0 && var.performance_threshold_cpu <= 100
    error_message = "CPU threshold must be between 1 and 100."
  }
}

variable "performance_threshold_memory" {
  description = "Memory utilization threshold for alerts (percentage)"
  type        = number
  default     = 85
  
  validation {
    condition     = var.performance_threshold_memory > 0 && var.performance_threshold_memory <= 100
    error_message = "Memory threshold must be between 1 and 100."
  }
}

variable "enable_disaster_recovery" {
  description = "Enable disaster recovery features"
  type        = bool
  default     = true
}

variable "rto_target_minutes" {
  description = "Recovery Time Objective target in minutes"
  type        = number
  default     = 30
  
  validation {
    condition     = var.rto_target_minutes > 0 && var.rto_target_minutes <= 1440
    error_message = "RTO target must be between 1 and 1440 minutes (24 hours)."
  }
}

variable "rpo_target_minutes" {
  description = "Recovery Point Objective target in minutes"
  type        = number
  default     = 5
  
  validation {
    condition     = var.rpo_target_minutes > 0 && var.rpo_target_minutes <= 60
    error_message = "RPO target must be between 1 and 60 minutes."
  }
}

variable "enable_compliance_monitoring" {
  description = "Enable compliance monitoring"
  type        = bool
  default     = true
}

variable "compliance_frameworks" {
  description = "List of compliance frameworks to monitor"
  type        = list(string)
  default     = ["SOC2", "ISO27001", "GDPR"]
  
  validation {
    condition = alltrue([
      for framework in var.compliance_frameworks : contains([
        "SOC2", "ISO27001", "GDPR", "HIPAA", "PCI-DSS", "FedRAMP"
      ], framework)
    ])
    error_message = "All compliance frameworks must be valid options."
  }
}
