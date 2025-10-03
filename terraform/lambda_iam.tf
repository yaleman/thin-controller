# IAM policy for Lambda to manage EC2 instances
resource "aws_iam_policy" "lambda_ec2_policy" {
  count       = var.use_lambda ? 1 : 0
  name        = "thin-controller-lambda-ec2-policy"
  description = "Allow Lambda to describe, start, and stop EC2 instances"

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
    local.common_tags,
    {
      Name = "thin-controller-lambda-ec2-policy"
    }
  )
}

# Attach the policy to the Lambda function role
resource "aws_iam_role_policy_attachment" "lambda_ec2_policy_attachment" {
  count      = var.use_lambda ? 1 : 0
  role       = module.thin_controller_module[0].lambda_role_name
  policy_arn = aws_iam_policy.lambda_ec2_policy[0].arn
}
