# ACGS Platform Terraform Module
# Comprehensive Infrastructure as Code for ACGS Platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Variables
variable "namespace" {
  description = "Kubernetes namespace for ACGS platform"
  type        = string
  default     = "acgs-production"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

variable "constitutional_hash" {
  description = "Constitutional compliance hash"
  type        = string
  default     = "cdd01ef066bc6cf2"
}

variable "replica_count" {
  description = "Number of replicas for each service"
  type        = number
  default     = 2
}

variable "resource_limits" {
  description = "Resource limits for services"
  type = object({
    cpu    = string
    memory = string
  })
  default = {
    cpu    = "2000m"
    memory = "4Gi"
  }
}

variable "resource_requests" {
  description = "Resource requests for services"
  type = object({
    cpu    = string
    memory = string
  })
  default = {
    cpu    = "500m"
    memory = "1Gi"
  }
}

# Namespace
resource "kubernetes_namespace" "acgs" {
  metadata {
    name = var.namespace
    labels = {
      environment = var.environment
      platform    = "acgs"
      managed-by  = "terraform"
    }
  }
}

# ConfigMap for ACGS Configuration
resource "kubernetes_config_map" "acgs_config" {
  metadata {
    name      = "acgs-config"
    namespace = kubernetes_namespace.acgs.metadata[0].name
  }

  data = {
    ENVIRONMENT         = var.environment
    CONSTITUTIONAL_HASH = var.constitutional_hash
    DATABASE_HOST       = "postgresql.${var.namespace}.svc.cluster.local"
    DATABASE_PORT       = "5432"
    REDIS_HOST          = "redis.${var.namespace}.svc.cluster.local"
    REDIS_PORT          = "6379"
    NATS_URL            = "nats://nats.${var.namespace}.svc.cluster.local:4222"
    OPA_URL             = "http://opa.${var.namespace}.svc.cluster.local:8181"
    LOG_LEVEL           = "INFO"
    METRICS_ENABLED     = "true"
    TRACING_ENABLED     = "true"
  }
}

# Secret for sensitive configuration
resource "random_password" "database_password" {
  length  = 32
  special = true
}

resource "kubernetes_secret" "acgs_secrets" {
  metadata {
    name      = "acgs-secrets"
    namespace = kubernetes_namespace.acgs.metadata[0].name
  }

  data = {
    DATABASE_PASSWORD = random_password.database_password.result
    JWT_SECRET        = random_password.database_password.result
    ENCRYPTION_KEY    = base64encode(random_password.database_password.result)
  }

  type = "Opaque"
}

# ACGS Services
locals {
  services = {
    auth-service = {
      port        = 8000
      image       = "acgs/auth-service"
      critical    = true
      health_path = "/health"
    }
    ac-service = {
      port        = 8001
      image       = "acgs/ac-service"
      critical    = true
      health_path = "/health"
    }
    integrity-service = {
      port        = 8002
      image       = "acgs/integrity-service"
      critical    = true
      health_path = "/health"
    }
    fv-service = {
      port        = 8003
      image       = "acgs/fv-service"
      critical    = false
      health_path = "/health"
    }
    gs-service = {
      port        = 8004
      image       = "acgs/gs-service"
      critical    = false
      health_path = "/health"
    }
    pgc-service = {
      port        = 8005
      image       = "acgs/pgc-service"
      critical    = false
      health_path = "/health"
    }
    ec-service = {
      port        = 8006
      image       = "acgs/ec-service"
      critical    = true
      health_path = "/health"
    }
  }
}

# Deployments for ACGS Services
resource "kubernetes_deployment" "acgs_services" {
  for_each = local.services

  metadata {
    name      = each.key
    namespace = kubernetes_namespace.acgs.metadata[0].name
    labels = {
      app         = each.key
      environment = var.environment
      critical    = tostring(each.value.critical)
    }
  }

  spec {
    replicas = var.replica_count

    selector {
      match_labels = {
        app = each.key
      }
    }

    template {
      metadata {
        labels = {
          app         = each.key
          environment = var.environment
          version     = "v1.0.0"
        }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = tostring(each.value.port)
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name  = each.key
          image = "${each.value.image}:latest"

          port {
            container_port = each.value.port
            name           = "http"
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.acgs_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.acgs_secrets.metadata[0].name
            }
          }

          resources {
            limits = {
              cpu    = var.resource_limits.cpu
              memory = var.resource_limits.memory
            }
            requests = {
              cpu    = var.resource_requests.cpu
              memory = var.resource_requests.memory
            }
          }

          liveness_probe {
            http_get {
              path = each.value.health_path
              port = each.value.port
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = each.value.health_path
              port = each.value.port
            }
            initial_delay_seconds = 5
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
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

        security_context {
          fs_group = 1000
        }

        restart_policy = "Always"
      }
    }

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_unavailable = "25%"
        max_surge       = "25%"
      }
    }
  }
}

# Services for ACGS Services
resource "kubernetes_service" "acgs_services" {
  for_each = local.services

  metadata {
    name      = each.key
    namespace = kubernetes_namespace.acgs.metadata[0].name
    labels = {
      app = each.key
    }
    annotations = {
      "prometheus.io/scrape" = "true"
      "prometheus.io/port"   = tostring(each.value.port)
    }
  }

  spec {
    selector = {
      app = each.key
    }

    port {
      name        = "http"
      port        = each.value.port
      target_port = each.value.port
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

# Horizontal Pod Autoscaler
resource "kubernetes_horizontal_pod_autoscaler_v2" "acgs_hpa" {
  for_each = { for k, v in local.services : k => v if v.critical }

  metadata {
    name      = "${each.key}-hpa"
    namespace = kubernetes_namespace.acgs.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = each.key
    }

    min_replicas = var.replica_count
    max_replicas = var.replica_count * 5

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}

# Network Policies
resource "kubernetes_network_policy" "acgs_network_policy" {
  metadata {
    name      = "acgs-network-policy"
    namespace = kubernetes_namespace.acgs.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        environment = var.environment
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            name = var.namespace
          }
        }
      }
    }

    egress {
      to {
        namespace_selector {
          match_labels = {
            name = var.namespace
          }
        }
      }
    }
  }
}

# Pod Disruption Budget
resource "kubernetes_pod_disruption_budget_v1" "acgs_pdb" {
  for_each = { for k, v in local.services : k => v if v.critical }

  metadata {
    name      = "${each.key}-pdb"
    namespace = kubernetes_namespace.acgs.metadata[0].name
  }

  spec {
    min_available = "50%"
    selector {
      match_labels = {
        app = each.key
      }
    }
  }
}

# Outputs
output "namespace" {
  description = "ACGS namespace"
  value       = kubernetes_namespace.acgs.metadata[0].name
}

output "services" {
  description = "ACGS services"
  value = {
    for k, v in kubernetes_service.acgs_services : k => {
      name = v.metadata[0].name
      port = v.spec[0].port[0].port
    }
  }
}

output "constitutional_hash" {
  description = "Constitutional compliance hash"
  value       = var.constitutional_hash
}
