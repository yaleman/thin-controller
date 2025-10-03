# WAF IP Set for allow list
resource "aws_wafv2_ip_set" "allow_list" {
  count              = var.use_fargate && length(var.ip_allow_list_inbound) > 0 ? 1 : 0
  name               = "thin-controller-ip-allow-list"
  description        = "IP addresses allowed to access thin-controller"
  scope              = "CLOUDFRONT"
  ip_address_version = "IPV4"
  addresses          = var.ip_allow_list_inbound
  provider           = aws.us-east-1

  tags = merge(
    local.common_tags,
    {
      Name = "thin-controller-ip-allow-list"
    }
  )
}

# WAF WebACL for CloudFront
resource "aws_wafv2_web_acl" "thin_controller" {
  count       = var.use_fargate ? 1 : 0
  name        = "thin-controller-waf"
  description = "WAF to block traffic from sanctioned countries and allow specific IPs"
  scope       = "CLOUDFRONT"
  provider    = aws.us-east-1

  default_action {
    allow {}
  }

  dynamic "rule" {
    for_each = length(var.ip_allow_list_inbound) > 0 ? [1] : []
    content {
      name     = "allow-ip-whitelist"
      priority = 0

      action {
        allow {}
      }

      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.allow_list[0].arn
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "allow-ip-whitelist"
        sampled_requests_enabled   = true
      }
    }
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

  tags = merge(
    local.common_tags,
    {
      Name = "thin-controller-waf"
    }
  )
}

# Output
output "waf_web_acl_arn" {
  description = "ARN of the WAF WebACL"
  value       = var.use_fargate ? aws_wafv2_web_acl.thin_controller[0].arn : null
}
