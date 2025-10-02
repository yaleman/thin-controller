# CloudFront distribution with WAF
resource "aws_cloudfront_distribution" "thin_controller" {
  count   = var.use_fargate ? 1 : 0
  enabled = true
  comment = "Thin Controller CloudFront distribution"

  origin {
    domain_name = aws_lb.thin_controller_nlb[0].dns_name
    origin_id   = "nlb-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "nlb-origin"

    forwarded_values {
      query_string = true
      headers      = ["*"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    compress               = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  web_acl_id = aws_wafv2_web_acl.thin_controller[0].arn

  tags = {
    Name = "thin-controller"
  }
}

# Output
output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.use_fargate ? aws_cloudfront_distribution.thin_controller[0].domain_name : null
}

output "cloudfront_url" {
  description = "CloudFront URL for accessing the application"
  value       = var.use_fargate ? "https://${aws_cloudfront_distribution.thin_controller[0].domain_name}" : null
}
