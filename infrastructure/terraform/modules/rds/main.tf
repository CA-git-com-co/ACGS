# ACGS-1 RDS Module
# PostgreSQL database infrastructure for ACGS-1 Constitutional Governance System

# DB Subnet Group
resource "aws_db_subnet_group" "acgs_db_subnet_group" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-db-subnet-group"
    Type = "Database"
  })
}

# DB Parameter Group
resource "aws_db_parameter_group" "acgs_db_parameter_group" {
  family = "postgres15"
  name   = "${var.name_prefix}-db-parameter-group"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "max_connections"
    value = var.environment == "production" ? "200" : "100"
  }

  parameter {
    name  = "work_mem"
    value = var.environment == "production" ? "16384" : "8192"
  }

  tags = var.tags
}

# Security Group for RDS
resource "aws_security_group" "rds_security_group" {
  name_prefix = "${var.name_prefix}-rds-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
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
    Name = "${var.name_prefix}-rds-security-group"
  })
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.name_prefix}-db-password"
  description             = "Database password for ACGS-1"
  recovery_window_in_days = var.environment == "production" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = var.username
    password = random_password.db_password.result
  })
}

# RDS Instance
resource "aws_db_instance" "acgs_database" {
  identifier = "${var.name_prefix}-database"

  # Engine configuration
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.instance_class

  # Storage configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 10
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds_key.arn

  # Database configuration
  db_name  = var.database_name
  username = var.username
  password = random_password.db_password.result

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.acgs_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_security_group.id]
  publicly_accessible    = false

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window
  copy_tags_to_snapshot  = true

  # Monitoring configuration
  monitoring_interval = var.monitoring_enabled ? 60 : 0
  monitoring_role_arn = var.monitoring_enabled ? aws_iam_role.rds_monitoring[0].arn : null

  # Performance Insights
  performance_insights_enabled = var.environment == "production"
  performance_insights_kms_key_id = var.environment == "production" ? aws_kms_key.rds_key.arn : null

  # Multi-AZ for production
  multi_az = var.environment == "production"

  # Deletion protection for production
  deletion_protection = var.environment == "production"

  # Parameter group
  parameter_group_name = aws_db_parameter_group.acgs_db_parameter_group.name

  # Enable automated minor version upgrades
  auto_minor_version_upgrade = true

  # Final snapshot
  final_snapshot_identifier = "${var.name_prefix}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  skip_final_snapshot       = var.environment != "production"

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-database"
    Type = "Primary Database"
  })
}

# Read Replica for production
resource "aws_db_instance" "acgs_database_replica" {
  count = var.environment == "production" ? 1 : 0

  identifier = "${var.name_prefix}-database-replica"

  # Replica configuration
  replicate_source_db = aws_db_instance.acgs_database.identifier

  # Instance configuration
  instance_class = var.instance_class

  # Network configuration
  publicly_accessible = false

  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring[0].arn

  # Performance Insights
  performance_insights_enabled = true
  performance_insights_kms_key_id = aws_kms_key.rds_key.arn

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-database-replica"
    Type = "Read Replica"
  })
}

# KMS Key for RDS encryption
resource "aws_kms_key" "rds_key" {
  description             = "KMS key for ACGS-1 RDS encryption"
  deletion_window_in_days = var.environment == "production" ? 30 : 7

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-rds-kms-key"
  })
}

resource "aws_kms_alias" "rds_key_alias" {
  name          = "alias/${var.name_prefix}-rds"
  target_key_id = aws_kms_key.rds_key.key_id
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  count = var.monitoring_enabled ? 1 : 0

  name = "${var.name_prefix}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.monitoring_enabled ? 1 : 0

  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "postgresql" {
  name              = "/aws/rds/instance/${aws_db_instance.acgs_database.identifier}/postgresql"
  retention_in_days = var.environment == "production" ? 30 : 7
  kms_key_id        = aws_kms_key.rds_key.arn

  tags = var.tags
}

# Data source for VPC
data "aws_vpc" "vpc" {
  id = var.vpc_id
}
