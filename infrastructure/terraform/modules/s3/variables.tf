# ACGS-1 S3 Module Variables

variable "name_prefix" {
  description = "Name prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "buckets" {
  description = "Map of S3 buckets to create"
  type = map(object({
    versioning      = bool
    encryption      = bool
    lifecycle_rules = bool
  }))
  default = {
    constitutional_documents = {
      versioning      = true
      encryption      = true
      lifecycle_rules = true
    }
    governance_artifacts = {
      versioning      = true
      encryption      = true
      lifecycle_rules = true
    }
    audit_logs = {
      versioning      = true
      encryption      = true
      lifecycle_rules = true
    }
    backups = {
      versioning      = true
      encryption      = true
      lifecycle_rules = true
    }
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
