# ACGS-1 Monitoring Module

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "acgs_logs" {
  for_each = toset([
    "auth-service",
    "ac-service", 
    "integrity-service",
    "fv-service",
    "gs-service",
    "pgc-service",
    "ec-service"
  ])

  name              = "/aws/acgs/${var.name_prefix}/${each.value}"
  retention_in_days = var.environment == "production" ? 30 : 7

  tags = merge(var.tags, {
    Name    = "${var.name_prefix}-${each.value}-logs"
    Service = each.value
  })
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "acgs_dashboard" {
  dashboard_name = "${var.name_prefix}-acgs-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/EKS", "cluster_failed_request_count", "ClusterName", var.cluster_name],
            [".", "cluster_request_total", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "EKS Cluster Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '/aws/acgs/${var.name_prefix}/auth-service' | fields @timestamp, @message | sort @timestamp desc | limit 100"
          region  = data.aws_region.current.name
          title   = "Recent Auth Service Logs"
        }
      }
    ]
  })

  tags = var.tags
}

# SNS Topic for Alerts
resource "aws_sns_topic" "acgs_alerts" {
  name         = "${var.name_prefix}-acgs-alerts"
  display_name = "ACGS Constitutional Governance Alerts"

  tags = var.tags
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  for_each = toset([
    "auth-service",
    "ac-service",
    "integrity-service", 
    "fv-service",
    "gs-service",
    "pgc-service",
    "ec-service"
  ])

  alarm_name          = "${var.name_prefix}-${each.value}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ErrorCount"
  namespace           = "ACGS/Services"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors error rate for ${each.value}"
  alarm_actions       = [aws_sns_topic.acgs_alerts.arn]

  dimensions = {
    ServiceName = each.value
    Environment = var.environment
  }

  tags = var.tags
}

# Data source for current region
data "aws_region" "current" {}
