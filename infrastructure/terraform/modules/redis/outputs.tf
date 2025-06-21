# ACGS-1 Redis Module Outputs

output "endpoint" {
  description = "Redis primary endpoint"
  value       = aws_elasticache_replication_group.acgs_redis.primary_endpoint_address
}

output "port" {
  description = "Redis port"
  value       = aws_elasticache_replication_group.acgs_redis.port
}

output "auth_token" {
  description = "Redis auth token"
  value       = random_password.redis_auth_token.result
  sensitive   = true
}

output "security_group_id" {
  description = "Security group ID for Redis"
  value       = aws_security_group.redis_security_group.id
}

output "subnet_group_name" {
  description = "ElastiCache subnet group name"
  value       = aws_elasticache_subnet_group.acgs_redis_subnet_group.name
}

output "kms_key_id" {
  description = "KMS key ID for Redis encryption"
  value       = aws_kms_key.redis_key.key_id
}

output "secret_arn" {
  description = "ARN of the secret containing Redis auth token"
  value       = aws_secretsmanager_secret.redis_auth_token.arn
}
