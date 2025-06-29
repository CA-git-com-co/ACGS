# Temporary AWS WAFv2 Web ACL with basic SQL injection rules

variable "enable_waf" {
  type        = bool
  description = "Enable AWS WAF"
  default     = true
}

resource "aws_wafv2_web_acl" "acgs_temp" {
  count       = var.enable_waf ? 1 : 0
  name        = "acgs-temp-waf"
  description = "Temporary WAF for SQL injection protection"
  scope       = "REGIONAL"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "acgs-temp-waf"
    sampled_requests_enabled   = true
  }
  rule {
    name     = "BlockSQLi"
    priority = 1
    statement {
      sqli_match_statement {
        field_to_match { all_query_arguments {} }
        text_transformation {
          priority = 0
          type     = "URL_DECODE"
        }
      }
    }
    action { block {} }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "acgs-sqli"
      sampled_requests_enabled   = true
    }
  }
}

output "waf_web_acl_arn" {
  value = aws_wafv2_web_acl.acgs_temp[0].arn
  description = "ARN of the temporary WAF Web ACL"
  condition   = var.enable_waf
}
