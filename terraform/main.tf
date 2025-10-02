# generate a layer for the thing
locals {
  thin_controller_layer_zip = "thin_controller_layer.zip"
}

resource "terraform_data" "thin_controller_layer" {
  triggers_replace = data.archive_file.thin_controller_layer

  provisioner "local-exec" {
    command = "python3.13 -m pip install --upgrade -t ./thin_controller_layer/ ../"
  }

}

data "archive_file" "thin_controller_layer" {
  type        = "zip"
  output_path = local.thin_controller_layer_zip
  source_dir  = "./thin_controller_layer"
}
resource "aws_lambda_layer_version" "thin_controller" {
  filename   = local.thin_controller_layer_zip
  layer_name = "thin_controller"

  compatible_runtimes = [
    "python3.13"
  ]
}

# lambda
module "thin_controller_module" {
  source = "git::https://github.com/yaleman/terraform_lambda?ref=1.0.8"

  function_name  = "thin_controller"
  lambda_handler = "handler.handler"
  lambda_runtime = "python3.13"

  aws_region     = var.aws_region
  aws_profile    = var.aws_profile
  lambda_timeout = 30
  layer_arns = [
    aws_lambda_layer_version.thin_controller.arn
  ]
  lambda_script_filename = "../thin_controller/handler.py"

  environment_variables = {
    THIN_CONTROLLER_REGIONS = var.thin_controller_regions
  }
  log_retention_days = 7
}

# resource "aws_cloudfront_distribution" "thin_controller" {
#   aliases = [
#     var.public_hostname
#   ]
#   enabled = true
#   origin_group {
#     origin_id = "thin_controller"

#     failover_criteria {
#       status_codes = [403, 404, 500, 502]
#     }

#     member {
#       origin_id = "function_url"
#     }

#     # member {
#     #   origin_id = "failoverS3"
#     # }
#   }

#   origin {
#     domain_name = aws_lambda_function_url.thin_controller.function_url
#     origin_id   = "function_url"

#     # s3_origin_config {
#     #   origin_access_identity = aws_cloudfront_origin_access_identity.default.cloudfront_access_identity_path
#     # }
#   }

#   # origin {
#   #   domain_name = aws_s3_bucket.failover.bucket_regional_domain_name
#   #   origin_id   = "failoverS3"

#   #   s3_origin_config {
#   #     origin_access_identity = aws_cloudfront_origin_access_identity.default.cloudfront_access_identity_path
#   #   }
#   # }

#   default_cache_behavior {
#     target_origin_id = "function_url"
#   }

#   restrictions {
#     geo_restriction {
#       # limit where it's distributed to
#       restriction_type = "whitelist"
#       locations = var.cloudfront_geo_regions
#     }
#   }

# }
