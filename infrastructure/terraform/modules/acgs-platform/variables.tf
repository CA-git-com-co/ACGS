# ACGS-2 Platform Module Variables
# Constitutional Hash: cdd01ef066bc6cf2

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "namespace" {
  description = "Kubernetes namespace for ACGS platform"
  type        = string
  default     = "acgs"
}

variable "constitutional_hash" {
  description = "Constitutional compliance hash"
  type        = string
  default     = "cdd01ef066bc6cf2"
  validation {
    condition     = can(regex("^[a-f0-9]{16}$", var.constitutional_hash))
    error_message = "Constitutional hash must be a 16-character hexadecimal string."
  }
}

variable "acgs_version" {
  description = "ACGS platform version"
  type        = string
  default     = "latest"
}

variable "container_registry" {
  description = "Container registry for ACGS images"
  type        = string
  default     = "ghcr.io/acgs"
}

variable "log_level" {
  description = "Log level for ACGS services"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

variable "debug" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

# Database Configuration
variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgres_storage_size" {
  description = "PostgreSQL storage size"
  type        = string
  default     = "20Gi"
}

variable "postgres_memory_limit" {
  description = "PostgreSQL memory limit"
  type        = string
  default     = "2Gi"
}

variable "postgres_cpu_limit" {
  description = "PostgreSQL CPU limit"
  type        = string
  default     = "1000m"
}

variable "postgres_memory_request" {
  description = "PostgreSQL memory request"
  type        = string
  default     = "1Gi"
}

variable "postgres_cpu_request" {
  description = "PostgreSQL CPU request"
  type        = string
  default     = "500m"
}

# Redis Configuration
variable "redis_password" {
  description = "Redis password"
  type        = string
  sensitive   = true
}

variable "redis_storage_size" {
  description = "Redis storage size"
  type        = string
  default     = "10Gi"
}

variable "redis_memory_limit" {
  description = "Redis memory limit"
  type        = string
  default     = "1Gi"
}

variable "redis_cpu_limit" {
  description = "Redis CPU limit"
  type        = string
  default     = "500m"
}

variable "redis_memory_request" {
  description = "Redis memory request"
  type        = string
  default     = "512Mi"
}

variable "redis_cpu_request" {
  description = "Redis CPU request"
  type        = string
  default     = "250m"
}

# Constitutional AI Service Configuration
variable "constitutional_ai_replicas" {
  description = "Number of Constitutional AI replicas"
  type        = number
  default     = 2
}

variable "constitutional_ai_min_replicas" {
  description = "Minimum number of Constitutional AI replicas for HPA"
  type        = number
  default     = 2
}

variable "constitutional_ai_max_replicas" {
  description = "Maximum number of Constitutional AI replicas for HPA"
  type        = number
  default     = 10
}

variable "constitutional_ai_memory_limit" {
  description = "Constitutional AI memory limit"
  type        = string
  default     = "2Gi"
}

variable "constitutional_ai_cpu_limit" {
  description = "Constitutional AI CPU limit"
  type        = string
  default     = "1000m"
}

variable "constitutional_ai_memory_request" {
  description = "Constitutional AI memory request"
  type        = string
  default     = "1Gi"
}

variable "constitutional_ai_cpu_request" {
  description = "Constitutional AI CPU request"
  type        = string
  default     = "500m"
}

# API Keys (Sensitive)
variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "groq_api_key" {
  description = "Groq API key"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable Prometheus monitoring"
  type        = bool
  default     = true
}

variable "enable_istio" {
  description = "Enable Istio service mesh"
  type        = bool
  default     = false
}

variable "enable_autoscaling" {
  description = "Enable horizontal pod autoscaling"
  type        = bool
  default     = true
}

# Performance Targets
variable "performance_targets" {
  description = "Performance targets for ACGS services"
  type = object({
    p99_latency_ms    = number
    throughput_rps    = number
    cache_hit_rate    = number
  })
  default = {
    p99_latency_ms    = 5
    throughput_rps    = 100
    cache_hit_rate    = 0.85
  }
}

# Security Configuration
variable "enable_network_policies" {
  description = "Enable Kubernetes network policies"
  type        = bool
  default     = true
}

variable "enable_pod_security_policies" {
  description = "Enable pod security policies"
  type        = bool
  default     = true
}

variable "enable_rbac" {
  description = "Enable RBAC"
  type        = bool
  default     = true
}

# Backup Configuration
variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

# Multi-region Configuration
variable "enable_multi_region" {
  description = "Enable multi-region deployment"
  type        = bool
  default     = false
}

variable "regions" {
  description = "List of regions for multi-region deployment"
  type        = list(string)
  default     = ["us-east-1"]
}

# Tags
variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    "Project"             = "ACGS-2"
    "ManagedBy"          = "Terraform"
    "ConstitutionalHash" = "cdd01ef066bc6cf2"
  }
}
