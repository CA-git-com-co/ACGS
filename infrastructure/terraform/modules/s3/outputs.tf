# ACGS-1 S3 Module Outputs

output "bucket_names" {
  description = "Map of bucket names"
  value       = { for k, v in aws_s3_bucket.acgs_buckets : k => v.id }
}

output "bucket_arns" {
  description = "Map of bucket ARNs"
  value       = { for k, v in aws_s3_bucket.acgs_buckets : k => v.arn }
}

output "bucket_domain_names" {
  description = "Map of bucket domain names"
  value       = { for k, v in aws_s3_bucket.acgs_buckets : k => v.bucket_domain_name }
}

output "kms_key_id" {
  description = "KMS key ID for S3 encryption"
  value       = aws_kms_key.s3_key.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for S3 encryption"
  value       = aws_kms_key.s3_key.arn
}

output "access_logs_bucket" {
  description = "Access logs bucket name"
  value       = aws_s3_bucket.access_logs.id
}
