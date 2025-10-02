# WAF WebACL for CloudFront
resource "aws_wafv2_web_acl" "thin_controller" {
  count       = var.use_fargate ? 1 : 0
  name        = "thin-controller-waf"
  description = "WAF to block traffic from sanctioned countries"
  scope       = "CLOUDFRONT"
  provider    = aws.us-east-1

  default_action {
    allow {}
  }

  rule {
    name     = "block-sanctioned-countries"
    priority = 1

    action {
      block {}
    }

    statement {
      geo_match_statement {
        country_codes = ["SY", "SD", "RU", "KP", "IR", "CU"]
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "block-sanctioned-countries"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "thin-controller-waf"
    sampled_requests_enabled   = true
  }

  tags = {
    Name = "thin-controller-waf"
  }
}

# Output
output "waf_web_acl_arn" {
  description = "ARN of the WAF WebACL"
  value       = var.use_fargate ? aws_wafv2_web_acl.thin_controller[0].arn : null
}
