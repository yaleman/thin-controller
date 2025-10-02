# ECS Cluster
resource "aws_ecs_cluster" "thin_controller" {
  count = var.use_fargate ? 1 : 0
  name  = "thin-controller"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  count = var.use_fargate ? 1 : 0
  name  = "thin-controller-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  count      = var.use_fargate ? 1 : 0
  role       = aws_iam_role.ecs_task_execution_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role for ECS Task (for the application itself to access AWS services)
resource "aws_iam_role" "ecs_task_role" {
  count = var.use_fargate ? 1 : 0
  name  = "thin-controller-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Policy to allow EC2 instance management
resource "aws_iam_role_policy" "ecs_task_ec2_policy" {
  count = var.use_fargate ? 1 : 0
  name  = "thin-controller-ec2-policy"
  role  = aws_iam_role.ecs_task_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Logs Group
resource "aws_cloudwatch_log_group" "thin_controller" {
  count             = var.use_fargate ? 1 : 0
  name              = "/ecs/thin-controller"
  retention_in_days = 7
}

# ECS Task Definition
resource "aws_ecs_task_definition" "thin_controller" {
  count                    = var.use_fargate ? 1 : 0
  family                   = "thin-controller"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role[0].arn
  task_role_arn            = aws_iam_role.ecs_task_role[0].arn

  container_definitions = jsonencode([
    {
      name      = "thin-controller"
      image     = "ghcr.io/yaleman/thin-controller:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "THIN_CONTROLLER_REGIONS"
          value = var.thin_controller_regions
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.thin_controller[0].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  count       = var.use_fargate ? 1 : 0
  name        = "thin-controller-ecs-tasks"
  description = "Security group for thin-controller ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTP from NLB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "thin-controller-ecs-tasks"
  }
}

# Network Load Balancer
resource "aws_lb" "thin_controller_nlb" {
  count              = var.use_fargate ? 1 : 0
  name               = "thin-controller-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = var.public_subnet_ids

  tags = {
    Name = "thin-controller-nlb"
  }
}

# Target Group (NLB)
resource "aws_lb_target_group" "thin_controller_nlb" {
  count       = var.use_fargate ? 1 : 0
  name        = "thin-controller-nlb"
  port        = 8000
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    port                = "traffic-port"
    protocol            = "TCP"
    unhealthy_threshold = 3
  }

  tags = {
    Name = "thin-controller-nlb"
  }
}

# NLB Listener
resource "aws_lb_listener" "thin_controller_nlb" {
  count             = var.use_fargate ? 1 : 0
  load_balancer_arn = aws_lb.thin_controller_nlb[0].arn
  port              = "80"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.thin_controller_nlb[0].arn
  }
}

# ECS Service
resource "aws_ecs_service" "thin_controller" {
  count           = var.use_fargate ? 1 : 0
  name            = "thin-controller"
  cluster         = aws_ecs_cluster.thin_controller[0].id
  task_definition = aws_ecs_task_definition.thin_controller[0].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks[0].id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.thin_controller_nlb[0].arn
    container_name   = "thin-controller"
    container_port   = 8000
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]
}

# Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = var.use_fargate ? aws_ecs_cluster.thin_controller[0].name : null
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = var.use_fargate ? aws_ecs_service.thin_controller[0].name : null
}

output "nlb_dns_name" {
  description = "DNS name of the Network Load Balancer"
  value       = var.use_fargate ? aws_lb.thin_controller_nlb[0].dns_name : null
}

output "connection_info" {
  description = "How to connect to the application"
  value       = var.use_fargate ? "Use CloudFront URL (see cloudfront_url output)" : null
}
