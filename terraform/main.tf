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
  count       = var.use_lambda ? 1 : 0
  type        = "zip"
  output_path = local.thin_controller_layer_zip
  source_dir  = "./thin_controller_layer"
}
resource "aws_lambda_layer_version" "thin_controller" {
  count      = var.use_lambda ? 1 : 0
  filename   = local.thin_controller_layer_zip
  layer_name = "thin_controller"

  compatible_runtimes = [
    "python3.12"
  ]
}

# lambda
module "thin_controller_module" {
  count  = var.use_lambda ? 1 : 0
  source = "git::https://github.com/yaleman/terraform_lambda?ref=1.0.8"

  function_name  = "thin_controller"
  lambda_handler = "handler.handler"
  lambda_runtime = "python3.12"

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
