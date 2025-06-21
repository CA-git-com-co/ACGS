# ACGS-1 Monitoring Module Outputs

output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.acgs_dashboard.dashboard_name}"
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.acgs_alerts.arn
}

output "log_groups" {
  description = "Map of log group names"
  value       = { for k, v in aws_cloudwatch_log_group.acgs_logs : k => v.name }
}

# Data source for current region
data "aws_region" "current" {}
