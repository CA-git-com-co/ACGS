# ACGS Production Environment Variables

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
  default     = "admin123"
}

variable "smtp_smarthost" {
  description = "SMTP server for alerting"
  type        = string
  default     = "localhost:587"
}

variable "smtp_from" {
  description = "From email address for alerts"
  type        = string
  default     = "alerts@acgs.local"
}

variable "kubernetes_config_path" {
  description = "Path to Kubernetes config file"
  type        = string
  default     = "~/.kube/config"
}

variable "enable_monitoring" {
  description = "Enable monitoring stack"
  type        = bool
  default     = true
}

variable "enable_security" {
  description = "Enable security features"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable backup and disaster recovery"
  type        = bool
  default     = true
}
