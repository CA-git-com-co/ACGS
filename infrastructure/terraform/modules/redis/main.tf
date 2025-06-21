# ACGS-1 Redis Module
# ElastiCache Redis infrastructure for ACGS-1 Constitutional Governance System

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "acgs_redis_subnet_group" {
  name       = "${var.name_prefix}-redis-subnet-group"
  subnet_ids = var.subnet_ids

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis-subnet-group"
  })
}

# Security Group for Redis
resource "aws_security_group" "redis_security_group" {
  name_prefix = "${var.name_prefix}-redis-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.vpc.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis-security-group"
  })
}

# KMS Key for Redis encryption
resource "aws_kms_key" "redis_key" {
  description             = "KMS key for ACGS-1 Redis encryption"
  deletion_window_in_days = var.environment == "production" ? 30 : 7

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis-kms-key"
  })
}

resource "aws_kms_alias" "redis_key_alias" {
  name          = "alias/${var.name_prefix}-redis"
  target_key_id = aws_kms_key.redis_key.key_id
}

# Redis Parameter Group
resource "aws_elasticache_parameter_group" "acgs_redis_parameter_group" {
  family = "redis7.x"
  name   = "${var.name_prefix}-redis-parameter-group"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }

  tags = var.tags
}

# Redis Replication Group (Cluster)
resource "aws_elasticache_replication_group" "acgs_redis" {
  replication_group_id         = "${var.name_prefix}-redis"
  description                  = "ACGS-1 Redis cluster for constitutional governance caching"

  # Node configuration
  node_type               = var.node_type
  port                   = 6379
  parameter_group_name   = aws_elasticache_parameter_group.acgs_redis_parameter_group.name

  # Cluster configuration
  num_cache_clusters = var.num_cache_nodes

  # Network configuration
  subnet_group_name  = aws_elasticache_subnet_group.acgs_redis_subnet_group.name
  security_group_ids = [aws_security_group.redis_security_group.id]

  # Encryption configuration
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  kms_key_id                 = aws_kms_key.redis_key.arn

  # Auth token for encryption in transit
  auth_token = random_password.redis_auth_token.result

  # Backup configuration
  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window         = "03:00-05:00"

  # Maintenance configuration
  maintenance_window = "sun:05:00-sun:07:00"

  # Automatic failover for multi-node clusters
  automatic_failover_enabled = var.num_cache_nodes > 1

  # Multi-AZ for production
  multi_az_enabled = var.environment == "production" && var.num_cache_nodes > 1

  # Log delivery configuration
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis-cluster"
    Type = "Cache Cluster"
  })
}

# Random auth token for Redis
resource "random_password" "redis_auth_token" {
  length  = 64
  special = false  # Redis auth token cannot contain special characters
}

# Store auth token in AWS Secrets Manager
resource "aws_secretsmanager_secret" "redis_auth_token" {
  name                    = "${var.name_prefix}-redis-auth-token"
  description             = "Redis auth token for ACGS-1"
  recovery_window_in_days = var.environment == "production" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  secret_id = aws_secretsmanager_secret.redis_auth_token.id
  secret_string = jsonencode({
    auth_token = random_password.redis_auth_token.result
  })
}

# CloudWatch Log Group for Redis slow log
resource "aws_cloudwatch_log_group" "redis_slow_log" {
  name              = "/aws/elasticache/redis/${var.name_prefix}/slow-log"
  retention_in_days = var.environment == "production" ? 30 : 7
  kms_key_id        = aws_kms_key.redis_key.arn

  tags = var.tags
}

# CloudWatch Alarms for Redis
resource "aws_cloudwatch_metric_alarm" "redis_cpu_utilization" {
  alarm_name          = "${var.name_prefix}-redis-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors redis cpu utilization"
  alarm_actions       = var.environment == "production" ? [aws_sns_topic.redis_alerts[0].arn] : []

  dimensions = {
    CacheClusterId = "${aws_elasticache_replication_group.acgs_redis.replication_group_id}-001"
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "redis_memory_utilization" {
  alarm_name          = "${var.name_prefix}-redis-memory-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors redis memory utilization"
  alarm_actions       = var.environment == "production" ? [aws_sns_topic.redis_alerts[0].arn] : []

  dimensions = {
    CacheClusterId = "${aws_elasticache_replication_group.acgs_redis.replication_group_id}-001"
  }

  tags = var.tags
}

# SNS Topic for Redis alerts (production only)
resource "aws_sns_topic" "redis_alerts" {
  count = var.environment == "production" ? 1 : 0

  name         = "${var.name_prefix}-redis-alerts"
  display_name = "ACGS-1 Redis Alerts"
  kms_master_key_id = aws_kms_key.redis_key.arn

  tags = var.tags
}

# Data source for VPC
data "aws_vpc" "vpc" {
  id = var.vpc_id
}
