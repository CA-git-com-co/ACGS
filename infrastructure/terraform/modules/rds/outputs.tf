# ACGS-1 RDS Module Outputs

output "endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.acgs_database.endpoint
}

output "port" {
  description = "RDS instance port"
  value       = aws_db_instance.acgs_database.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.acgs_database.db_name
}

output "username" {
  description = "Database username"
  value       = aws_db_instance.acgs_database.username
}

output "password" {
  description = "Database password"
  value       = random_password.db_password.result
  sensitive   = true
}

output "replica_endpoint" {
  description = "Read replica endpoint"
  value       = var.environment == "production" ? aws_db_instance.acgs_database_replica[0].endpoint : null
}

output "security_group_id" {
  description = "Security group ID for RDS"
  value       = aws_security_group.rds_security_group.id
}

output "subnet_group_name" {
  description = "DB subnet group name"
  value       = aws_db_subnet_group.acgs_db_subnet_group.name
}

output "kms_key_id" {
  description = "KMS key ID for RDS encryption"
  value       = aws_kms_key.rds_key.key_id
}

output "secret_arn" {
  description = "ARN of the secret containing database credentials"
  value       = aws_secretsmanager_secret.db_password.arn
}
