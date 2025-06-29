# ACGS Backup Module
# Comprehensive backup and disaster recovery infrastructure

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Variables
variable "namespace" {
  description = "Kubernetes namespace for ACGS"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "backup_schedule" {
  description = "Backup schedule in cron format"
  type        = string
  default     = "0 */6 * * *"
}

variable "backup_retention" {
  description = "Backup retention period"
  type        = string
  default     = "30d"
}

variable "backup_storage_size" {
  description = "Backup storage size"
  type        = string
  default     = "500Gi"
}

# Backup Storage
resource "kubernetes_persistent_volume_claim" "backup_storage" {
  metadata {
    name      = "acgs-backup-storage"
    namespace = var.namespace
    labels = {
      app         = "acgs-backup"
      environment = var.environment
    }
  }

  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = "fast-ssd"
    
    resources {
      requests = {
        storage = var.backup_storage_size
      }
    }
  }
}

# Backup ConfigMap
resource "kubernetes_config_map" "backup_config" {
  metadata {
    name      = "acgs-backup-config"
    namespace = var.namespace
  }

  data = {
    BACKUP_SCHEDULE     = var.backup_schedule
    BACKUP_RETENTION    = var.backup_retention
    BACKUP_COMPRESSION  = "true"
    BACKUP_ENCRYPTION   = "true"
    BACKUP_VERIFICATION = "true"
    RTO_TARGET          = "1800"
    RPO_TARGET          = "300"
  }
}

# Backup CronJob
resource "kubernetes_cron_job_v1" "backup_cronjob" {
  metadata {
    name      = "acgs-backup-cronjob"
    namespace = var.namespace
    labels = {
      app         = "acgs-backup"
      environment = var.environment
    }
  }

  spec {
    schedule                      = var.backup_schedule
    successful_jobs_history_limit = 3
    failed_jobs_history_limit     = 1

    job_template {
      metadata {
        labels = {
          app = "acgs-backup"
        }
      }

      spec {
        template {
          metadata {
            labels = {
              app = "acgs-backup"
            }
          }

          spec {
            restart_policy = "OnFailure"

            container {
              name  = "backup"
              image = "acgs/disaster-recovery:latest"

              env_from {
                config_map_ref {
                  name = kubernetes_config_map.backup_config.metadata[0].name
                }
              }

              volume_mount {
                name       = "backup-storage"
                mount_path = "/backups"
              }

              volume_mount {
                name       = "backup-scripts"
                mount_path = "/scripts"
                read_only  = true
              }

              command = ["/scripts/disaster_recovery_automation.py", "backup"]

              resources {
                limits = {
                  cpu    = "1000m"
                  memory = "2Gi"
                }
                requests = {
                  cpu    = "500m"
                  memory = "1Gi"
                }
              }

              security_context {
                run_as_non_root = true
                run_as_user     = 1000
                capabilities {
                  drop = ["ALL"]
                }
                read_only_root_filesystem = true
              }
            }

            volume {
              name = "backup-storage"
              persistent_volume_claim {
                claim_name = kubernetes_persistent_volume_claim.backup_storage.metadata[0].name
              }
            }

            volume {
              name = "backup-scripts"
              config_map {
                name         = "acgs-backup-scripts"
                default_mode = "0755"
              }
            }
          }
        }
      }
    }
  }
}

# Backup Scripts ConfigMap
resource "kubernetes_config_map" "backup_scripts" {
  metadata {
    name      = "acgs-backup-scripts"
    namespace = var.namespace
  }

  data = {
    "disaster_recovery_automation.py" = file("${path.module}/../../../operational-excellence/scripts/disaster_recovery_automation.py")
  }
}

# Recovery Job Template
resource "kubernetes_job_v1" "recovery_job_template" {
  metadata {
    name      = "acgs-recovery-template"
    namespace = var.namespace
    labels = {
      app         = "acgs-recovery"
      environment = var.environment
    }
  }

  spec {
    template {
      metadata {
        labels = {
          app = "acgs-recovery"
        }
      }

      spec {
        restart_policy = "Never"

        container {
          name  = "recovery"
          image = "acgs/disaster-recovery:latest"

          env_from {
            config_map_ref {
              name = kubernetes_config_map.backup_config.metadata[0].name
            }
          }

          volume_mount {
            name       = "backup-storage"
            mount_path = "/backups"
            read_only  = true
          }

          volume_mount {
            name       = "recovery-scripts"
            mount_path = "/scripts"
            read_only  = true
          }

          command = ["/scripts/disaster_recovery_automation.py", "recover"]

          resources {
            limits = {
              cpu    = "2000m"
              memory = "4Gi"
            }
            requests = {
              cpu    = "1000m"
              memory = "2Gi"
            }
          }

          security_context {
            run_as_non_root = true
            run_as_user     = 1000
            capabilities {
              drop = ["ALL"]
            }
            read_only_root_filesystem = true
          }
        }

        volume {
          name = "backup-storage"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.backup_storage.metadata[0].name
          }
        }

        volume {
          name = "recovery-scripts"
          config_map {
            name         = "acgs-backup-scripts"
            default_mode = "0755"
          }
        }
      }
    }
  }

  wait_for_completion = false
}

# Outputs
output "backup_storage_claim" {
  description = "Backup storage claim name"
  value       = kubernetes_persistent_volume_claim.backup_storage.metadata[0].name
}

output "backup_schedule" {
  description = "Backup schedule"
  value       = var.backup_schedule
}

output "backup_retention" {
  description = "Backup retention period"
  value       = var.backup_retention
}
