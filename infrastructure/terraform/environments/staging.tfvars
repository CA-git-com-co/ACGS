# ACGS-1 Staging Environment Variables

# Environment Configuration
environment = "staging"
aws_region  = "us-west-2"

# Network Configuration
vpc_cidr = "10.1.0.0/16"

# Kubernetes Configuration
kubernetes_version = "1.28"
cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]

# Database Configuration
db_instance_class           = "db.r6g.large"
db_allocated_storage        = 200
db_backup_retention_period  = 14
db_deletion_protection      = true
db_multi_az                = true
db_monitoring_enabled      = true

# Redis Configuration
redis_node_type        = "cache.r6g.large"
redis_num_cache_nodes  = 2

# Security Configuration
enable_waf       = true
enable_shield    = false
enable_guardduty = true
enable_config    = true
enable_cloudtrail = true

# Monitoring Configuration
enable_prometheus    = true
enable_grafana      = true
enable_alertmanager = true
enable_jaeger       = true
enable_elk_stack    = true

# Cost Optimization
enable_spot_instances = false
spot_instance_types   = ["t3.large", "m5.large"]

# Performance Targets (Production-like)
performance_targets = {
  response_time_ms     = 1000
  availability_percent = 99.5
  concurrent_users     = 500
  throughput_rps      = 75
}

# Feature Flags
feature_flags = {
  blue_green_deployment     = true
  intelligent_alerting     = true
  automated_remediation    = false
  constitutional_validation = true
  multi_model_consensus    = true
  predictive_analytics     = false
  quantum_resistance       = false
}

# Additional Tags
additional_tags = {
  CostCenter = "Staging"
  Owner      = "Platform-Team"
  Purpose    = "Pre-Production-Testing"
}
