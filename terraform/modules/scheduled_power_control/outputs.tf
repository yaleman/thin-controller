output "eventbridge_rule_name" {
  value = "${var.function_name}_schedule"
}

output "lambda_function_name" {
  value = module.scheduler_lambda.lambda_function_name
}
