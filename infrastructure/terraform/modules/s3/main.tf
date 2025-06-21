# ACGS-1 S3 Module
# S3 bucket infrastructure for ACGS-1 Constitutional Governance System

# KMS Key for S3 encryption
resource "aws_kms_key" "s3_key" {
  description             = "KMS key for ACGS-1 S3 encryption"
  deletion_window_in_days = var.environment == "production" ? 30 : 7

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow S3 Service"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-s3-kms-key"
  })
}

resource "aws_kms_alias" "s3_key_alias" {
  name          = "alias/${var.name_prefix}-s3"
  target_key_id = aws_kms_key.s3_key.key_id
}

# S3 Buckets
resource "aws_s3_bucket" "acgs_buckets" {
  for_each = var.buckets

  bucket = "${var.name_prefix}-${each.key}"

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-${each.key}"
    BucketType  = each.key
    Environment = var.environment
  })
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "acgs_bucket_versioning" {
  for_each = var.buckets

  bucket = aws_s3_bucket.acgs_buckets[each.key].id
  versioning_configuration {
    status = each.value.versioning ? "Enabled" : "Suspended"
  }
}

# S3 Bucket Server-side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "acgs_bucket_encryption" {
  for_each = var.buckets

  bucket = aws_s3_bucket.acgs_buckets[each.key].id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = each.value.encryption ? aws_kms_key.s3_key.arn : null
      sse_algorithm     = each.value.encryption ? "aws:kms" : "AES256"
    }
    bucket_key_enabled = each.value.encryption
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "acgs_bucket_pab" {
  for_each = var.buckets

  bucket = aws_s3_bucket.acgs_buckets[each.key].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "acgs_bucket_lifecycle" {
  for_each = { for k, v in var.buckets : k => v if v.lifecycle_rules }

  bucket = aws_s3_bucket.acgs_buckets[each.key].id

  rule {
    id     = "constitutional_documents_lifecycle"
    status = "Enabled"

    # Transition to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete non-current versions after 90 days
    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    # Delete incomplete multipart uploads after 7 days
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # Special rule for audit logs
  dynamic "rule" {
    for_each = each.key == "audit_logs" ? [1] : []
    content {
      id     = "audit_logs_retention"
      status = "Enabled"

      # Keep audit logs for 7 years (2555 days) as per compliance requirements
      expiration {
        days = 2555
      }

      # Transition to IA after 90 days
      transition {
        days          = 90
        storage_class = "STANDARD_IA"
      }

      # Transition to Glacier after 365 days
      transition {
        days          = 365
        storage_class = "GLACIER"
      }
    }
  }
}

# S3 Bucket Notification for constitutional documents
resource "aws_s3_bucket_notification" "constitutional_documents_notification" {
  count = contains(keys(var.buckets), "constitutional_documents") ? 1 : 0

  bucket = aws_s3_bucket.acgs_buckets["constitutional_documents"].id

  eventbridge = true

  depends_on = [aws_s3_bucket.acgs_buckets]
}

# S3 Bucket Policy for constitutional documents
resource "aws_s3_bucket_policy" "constitutional_documents_policy" {
  count = contains(keys(var.buckets), "constitutional_documents") ? 1 : 0

  bucket = aws_s3_bucket.acgs_buckets["constitutional_documents"].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureConnections"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.acgs_buckets["constitutional_documents"].arn,
          "${aws_s3_bucket.acgs_buckets["constitutional_documents"].arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Sid    = "RequireSSEKMS"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:PutObject"
        Resource = "${aws_s3_bucket.acgs_buckets["constitutional_documents"].arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "aws:kms"
          }
        }
      }
    ]
  })
}

# CloudWatch Log Group for S3 access logs
resource "aws_cloudwatch_log_group" "s3_access_logs" {
  name              = "/aws/s3/${var.name_prefix}/access-logs"
  retention_in_days = var.environment == "production" ? 90 : 30
  kms_key_id        = aws_kms_key.s3_key.arn

  tags = var.tags
}

# S3 Bucket for access logs
resource "aws_s3_bucket" "access_logs" {
  bucket = "${var.name_prefix}-access-logs"

  tags = merge(var.tags, {
    Name       = "${var.name_prefix}-access-logs"
    BucketType = "access-logs"
  })
}

resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs_encryption" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_key.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "access_logs_pab" {
  bucket = aws_s3_bucket.access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Logging
resource "aws_s3_bucket_logging" "acgs_bucket_logging" {
  for_each = var.buckets

  bucket = aws_s3_bucket.acgs_buckets[each.key].id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "${each.key}/"
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# S3 Bucket Metrics
resource "aws_s3_bucket_metric" "acgs_bucket_metrics" {
  for_each = var.buckets

  bucket = aws_s3_bucket.acgs_buckets[each.key].id
  name   = "entire-bucket"
}
