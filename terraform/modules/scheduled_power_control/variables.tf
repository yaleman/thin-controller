variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "common_tags" {
  description = "Common tags applied to created resources"
  type        = map(string)
}

variable "function_name" {
  description = "Scheduler Lambda function name"
  type        = string
}

variable "lambda_layer_arns" {
  description = "Lambda layers attached to the scheduler"
  type        = list(string)
  default     = []
}

variable "schedule_expression" {
  description = "EventBridge schedule for the scheduler Lambda"
  type        = string
}

variable "thin_controller_regions" {
  description = "Comma-delimited list of regions to scan and control"
  type        = string
  default     = ""
}
