# ACGS-1 Infrastructure as Code - Variables
# Terraform variables for ACGS-1 Constitutional Governance System

# Environment Configuration
variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-west-2"
}

variable "constitutional_hash" {
  description = "Constitutional hash for governance validation"
  type        = string
  default     = "cdd01ef066bc6cf2"
  
  validation {
    condition     = length(var.constitutional_hash) == 15
    error_message = "Constitutional hash must be exactly 15 characters."
  }
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

# Kubernetes Configuration
variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "cluster_endpoint_private_access" {
  description = "Enable private API server endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access" {
  description = "Enable public API server endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "List of CIDR blocks that can access the public API server endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# Node Group Configuration
variable "node_groups" {
  description = "EKS node group configurations"
  type = map(object({
    instance_types = list(string)
    min_size      = number
    max_size      = number
    desired_size  = number
    disk_size     = number
    labels        = map(string)
    taints        = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  
  default = {
    system = {
      instance_types = ["t3.medium"]
      min_size      = 1
      max_size      = 3
      desired_size  = 2
      disk_size     = 50
      labels = {
        role = "system"
      }
      taints = []
    }
    
    acgs_services = {
      instance_types = ["t3.large"]
      min_size      = 2
      max_size      = 10
      desired_size  = 3
      disk_size     = 100
      labels = {
        role = "acgs-services"
      }
      taints = []
    }
    
    governance = {
      instance_types = ["t3.xlarge"]
      min_size      = 1
      max_size      = 5
      desired_size  = 2
      disk_size     = 100
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
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
  
  validation {
    condition     = var.db_allocated_storage >= 20
    error_message = "Database allocated storage must be at least 20 GB."
  }
}

variable "db_max_allocated_storage" {
  description = "RDS maximum allocated storage in GB for autoscaling"
  type        = number
  default     = 1000
}

variable "db_backup_retention_period" {
  description = "Database backup retention period in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.db_backup_retention_period >= 1 && var.db_backup_retention_period <= 35
    error_message = "Backup retention period must be between 1 and 35 days."
  }
}

variable "db_backup_window" {
  description = "Database backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "db_maintenance_window" {
  description = "Database maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "db_deletion_protection" {
  description = "Enable deletion protection for RDS instance"
  type        = bool
  default     = true
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

variable "db_monitoring_enabled" {
  description = "Enable enhanced monitoring for RDS"
  type        = bool
  default     = true
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in Redis cluster"
  type        = number
  default     = 1
}

variable "redis_parameter_group_name" {
  description = "Redis parameter group name"
  type        = string
  default     = "default.redis7"
}

variable "redis_port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "redis_at_rest_encryption_enabled" {
  description = "Enable encryption at rest for Redis"
  type        = bool
  default     = true
}

variable "redis_transit_encryption_enabled" {
  description = "Enable encryption in transit for Redis"
  type        = bool
  default     = true
}

# Security Configuration
variable "enable_waf" {
  description = "Enable AWS WAF for application protection"
  type        = bool
  default     = true
}

variable "enable_shield" {
  description = "Enable AWS Shield Advanced for DDoS protection"
  type        = bool
  default     = false
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty for threat detection"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable AWS CloudTrail for audit logging"
  type        = bool
  default     = true
}

# Monitoring Configuration
variable "enable_prometheus" {
  description = "Enable Prometheus monitoring"
  type        = bool
  default     = true
}

variable "enable_grafana" {
  description = "Enable Grafana dashboards"
  type        = bool
  default     = true
}

variable "enable_alertmanager" {
  description = "Enable Alertmanager for alert routing"
  type        = bool
  default     = true
}

variable "enable_jaeger" {
  description = "Enable Jaeger for distributed tracing"
  type        = bool
  default     = true
}

variable "enable_elk_stack" {
  description = "Enable ELK stack for log aggregation"
  type        = bool
  default     = true
}

# Backup Configuration
variable "backup_schedule" {
  description = "Backup schedule for automated backups"
  type        = string
  default     = "cron(0 2 * * ? *)"  # Daily at 2 AM UTC
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 1
    error_message = "Backup retention must be at least 1 day."
  }
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "spot_instance_types" {
  description = "Instance types for spot instances"
  type        = list(string)
  default     = ["t3.medium", "t3.large", "m5.large"]
}

# Compliance Configuration
variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest for all storage"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Enable encryption in transit for all communications"
  type        = bool
  default     = true
}

variable "compliance_standards" {
  description = "List of compliance standards to adhere to"
  type        = list(string)
  default     = ["SOC2", "GDPR", "CONSTITUTIONAL_GOVERNANCE"]
}

# Performance Configuration
variable "performance_targets" {
  description = "Performance targets for the system"
  type = object({
    response_time_ms     = number
    availability_percent = number
    concurrent_users     = number
    throughput_rps      = number
  })
  
  default = {
    response_time_ms     = 500
    availability_percent = 99.9
    concurrent_users     = 1000
    throughput_rps      = 100
  }
}

# Constitutional Governance Configuration
variable "governance_config" {
  description = "Constitutional governance configuration"
  type = object({
    compliance_threshold    = number
    validation_enabled     = bool
    audit_trail_enabled    = bool
    stakeholder_notifications = bool
  })
  
  default = {
    compliance_threshold    = 0.95
    validation_enabled     = true
    audit_trail_enabled    = true
    stakeholder_notifications = true
  }
}

# Feature Flags
variable "feature_flags" {
  description = "Feature flags for enabling/disabling functionality"
  type = map(bool)
  
  default = {
    blue_green_deployment     = true
    intelligent_alerting     = true
    automated_remediation    = true
    constitutional_validation = true
    multi_model_consensus    = true
    predictive_analytics     = false
    quantum_resistance       = false
  }
}

# Resource Tagging
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
