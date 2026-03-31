module "scheduled_power_control" {
  count  = var.enable_scheduled_power_control ? 1 : 0
  source = "./modules/scheduled_power_control"

  aws_region              = var.aws_region
  common_tags             = local.common_tags
  function_name           = "thin_controller_schedule"
  lambda_layer_arns       = local.lambda_layer_required ? [aws_lambda_layer_version.thin_controller[0].arn] : []
  schedule_expression     = var.scheduled_power_control_expression
  thin_controller_regions = var.thin_controller_regions
}
