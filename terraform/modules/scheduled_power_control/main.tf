module "scheduler_lambda" {
  source = "git::https://github.com/yaleman/terraform_lambda?ref=1.0.9"

  function_name  = var.function_name
  lambda_handler = "scheduler_handler.handler"
  lambda_runtime = "python3.12"

  lambda_timeout = 30
  layer_arns     = var.lambda_layer_arns

  lambda_script_filename     = abspath("${path.root}/../thin_controller/scheduler_handler.py")
  lambda_run_on_schedule     = true
  lambda_schedule_expression = var.schedule_expression

  environment_variables = {
    THIN_CONTROLLER_REGIONS = var.thin_controller_regions
  }

  log_retention_days = 7
}

resource "aws_iam_policy" "scheduler_ec2_policy" {
  name        = "${var.function_name}-ec2-policy"
  description = "Allow scheduled power control to describe, start, and stop managed EC2 instances"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ec2:ResourceTag/thin_controller_managed" = "true"
          }
        }
      }
    ]
  })

  tags = merge(
    var.common_tags,
    {
      Name = "${var.function_name}-ec2-policy"
    }
  )
}

resource "aws_iam_role_policy_attachment" "scheduler_ec2_policy_attachment" {
  role       = module.scheduler_lambda.role_name
  policy_arn = aws_iam_policy.scheduler_ec2_policy.arn
}
