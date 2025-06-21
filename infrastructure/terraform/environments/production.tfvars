# ACGS-1 Production Environment Variables

# Environment Configuration
environment = "production"
aws_region  = "us-west-2"

# Network Configuration
vpc_cidr = "10.2.0.0/16"

# Kubernetes Configuration
kubernetes_version = "1.28"
cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]  # Should be restricted in real production

# Database Configuration
db_instance_class           = "db.r6g.xlarge"
db_allocated_storage        = 500
db_max_allocated_storage    = 2000
db_backup_retention_period  = 30
db_deletion_protection      = true
db_multi_az                = true
db_monitoring_enabled      = true

# Redis Configuration
redis_node_type        = "cache.r6g.large"
redis_num_cache_nodes  = 3

# Security Configuration
enable_waf       = true
enable_shield    = true
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
spot_instance_types   = ["m5.large", "m5.xlarge"]

# Performance Targets (Strict Production)
performance_targets = {
  response_time_ms     = 500
  availability_percent = 99.9
  concurrent_users     = 1000
  throughput_rps      = 100
}

# Governance Configuration
governance_config = {
  compliance_threshold      = 0.95
  validation_enabled       = true
  audit_trail_enabled      = true
  stakeholder_notifications = true
}

# Feature Flags
feature_flags = {
  blue_green_deployment     = true
  intelligent_alerting     = true
  automated_remediation    = true
  constitutional_validation = true
  multi_model_consensus    = true
  predictive_analytics     = true
  quantum_resistance       = false
}

# Compliance Standards
compliance_standards = ["SOC2", "GDPR", "HIPAA", "FEDRAMP", "CONSTITUTIONAL_GOVERNANCE"]

# Additional Tags
additional_tags = {
  CostCenter   = "Production"
  Owner        = "Platform-Team"
  Purpose      = "Production-Constitutional-Governance"
  Compliance   = "Required"
  Criticality  = "High"
}
