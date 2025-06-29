# ACGS Security Module
# Comprehensive security infrastructure including RBAC, Network Policies, and Pod Security

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

variable "enable_network_policies" {
  description = "Enable network policies"
  type        = bool
  default     = true
}

variable "enable_pod_security" {
  description = "Enable pod security standards"
  type        = bool
  default     = true
}

variable "enable_rbac" {
  description = "Enable RBAC"
  type        = bool
  default     = true
}

# Service Account for ACGS Services
resource "kubernetes_service_account" "acgs_service_account" {
  metadata {
    name      = "acgs-service-account"
    namespace = var.namespace
    labels = {
      app         = "acgs"
      environment = var.environment
    }
  }
}

# RBAC Role for ACGS Services
resource "kubernetes_role" "acgs_role" {
  count = var.enable_rbac ? 1 : 0

  metadata {
    name      = "acgs-role"
    namespace = var.namespace
  }

  rule {
    api_groups = [""]
    resources  = ["configmaps", "secrets"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = [""]
    resources  = ["pods"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["apps"]
    resources  = ["deployments"]
    verbs      = ["get", "list", "watch"]
  }
}

# RBAC Role Binding
resource "kubernetes_role_binding" "acgs_role_binding" {
  count = var.enable_rbac ? 1 : 0

  metadata {
    name      = "acgs-role-binding"
    namespace = var.namespace
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.acgs_role[0].metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.acgs_service_account.metadata[0].name
    namespace = var.namespace
  }
}

# Network Policy for ACGS Services
resource "kubernetes_network_policy" "acgs_network_policy" {
  count = var.enable_network_policies ? 1 : 0

  metadata {
    name      = "acgs-network-policy"
    namespace = var.namespace
  }

  spec {
    pod_selector {
      match_labels = {
        app = "acgs-service"
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

      from {
        namespace_selector {
          match_labels = {
            name = "monitoring"
          }
        }
      }

      ports {
        protocol = "TCP"
        port     = "8000"
      }
      ports {
        protocol = "TCP"
        port     = "8001"
      }
      ports {
        protocol = "TCP"
        port     = "8002"
      }
      ports {
        protocol = "TCP"
        port     = "8003"
      }
      ports {
        protocol = "TCP"
        port     = "8004"
      }
      ports {
        protocol = "TCP"
        port     = "8005"
      }
      ports {
        protocol = "TCP"
        port     = "8006"
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

      # Allow egress to database
      to {
        namespace_selector {
          match_labels = {
            name = "database"
          }
        }
      }

      # Allow egress to external services (DNS, etc.)
      to {}

      ports {
        protocol = "TCP"
        port     = "5432"  # PostgreSQL
      }
      ports {
        protocol = "TCP"
        port     = "6379"  # Redis
      }
      ports {
        protocol = "TCP"
        port     = "53"    # DNS
      }
      ports {
        protocol = "UDP"
        port     = "53"    # DNS
      }
      ports {
        protocol = "TCP"
        port     = "443"   # HTTPS
      }
      ports {
        protocol = "TCP"
        port     = "80"    # HTTP
      }
    }
  }
}

# Pod Security Policy (if supported)
resource "kubernetes_manifest" "acgs_pod_security_policy" {
  count = var.enable_pod_security ? 1 : 0

  manifest = {
    apiVersion = "policy/v1beta1"
    kind       = "PodSecurityPolicy"
    metadata = {
      name = "acgs-psp"
    }
    spec = {
      privileged                = false
      allowPrivilegeEscalation  = false
      requiredDropCapabilities  = ["ALL"]
      volumes = [
        "configMap",
        "emptyDir",
        "projected",
        "secret",
        "downwardAPI",
        "persistentVolumeClaim"
      ]
      runAsUser = {
        rule = "MustRunAsNonRoot"
      }
      seLinux = {
        rule = "RunAsAny"
      }
      fsGroup = {
        rule = "RunAsAny"
      }
    }
  }
}

# Security Context Constraints (OpenShift)
resource "kubernetes_manifest" "acgs_security_context_constraints" {
  count = var.enable_pod_security ? 1 : 0

  manifest = {
    apiVersion = "security.openshift.io/v1"
    kind       = "SecurityContextConstraints"
    metadata = {
      name = "acgs-scc"
    }
    allowHostDirVolumePlugin = false
    allowHostIPC             = false
    allowHostNetwork         = false
    allowHostPID             = false
    allowHostPorts           = false
    allowPrivilegedContainer = false
    allowedCapabilities      = []
    defaultAddCapabilities   = []
    requiredDropCapabilities = ["ALL"]
    runAsUser = {
      type = "MustRunAsNonRoot"
    }
    seLinuxContext = {
      type = "MustRunAs"
    }
    fsGroup = {
      type = "RunAsAny"
    }
    volumes = [
      "configMap",
      "downwardAPI",
      "emptyDir",
      "persistentVolumeClaim",
      "projected",
      "secret"
    ]
  }
}

# Outputs
output "service_account_name" {
  description = "ACGS service account name"
  value       = kubernetes_service_account.acgs_service_account.metadata[0].name
}

output "security_policies" {
  description = "Security policies applied"
  value = {
    network_policies = var.enable_network_policies
    pod_security     = var.enable_pod_security
    rbac            = var.enable_rbac
  }
}
