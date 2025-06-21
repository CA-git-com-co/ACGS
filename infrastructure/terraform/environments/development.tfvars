# ACGS-1 Development Environment Variables

# Environment Configuration
environment = "development"
aws_region  = "us-west-2"

# Network Configuration
vpc_cidr = "10.0.0.0/16"

# Kubernetes Configuration
kubernetes_version = "1.28"
cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]

# Database Configuration
db_instance_class           = "db.t3.medium"
db_allocated_storage        = 100
db_backup_retention_period  = 7
db_deletion_protection      = false
db_multi_az                = false
db_monitoring_enabled      = false

# Redis Configuration
redis_node_type        = "cache.t3.micro"
redis_num_cache_nodes  = 1

# Security Configuration
enable_waf       = false
enable_shield    = false
enable_guardduty = false
enable_config    = false
enable_cloudtrail = true

# Monitoring Configuration
enable_prometheus    = true
enable_grafana      = true
enable_alertmanager = false
enable_jaeger       = false
enable_elk_stack    = false

# Cost Optimization
enable_spot_instances = true
spot_instance_types   = ["t3.medium", "t3.large"]

# Performance Targets (Relaxed for Development)
performance_targets = {
  response_time_ms     = 2000
  availability_percent = 99.0
  concurrent_users     = 100
  throughput_rps      = 50
}

# Feature Flags
feature_flags = {
  blue_green_deployment     = false
  intelligent_alerting     = false
  automated_remediation    = false
  constitutional_validation = true
  multi_model_consensus    = false
  predictive_analytics     = false
  quantum_resistance       = false
}

# Additional Tags
additional_tags = {
  CostCenter = "Development"
  Owner      = "Development-Team"
  Purpose    = "Development-Testing"
}
