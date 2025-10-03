variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS profile"
  type        = string
}

variable "public_hostname" {
  description = "Public hostname for the thin controller"
  type        = string
}

variable "use_lambda" {
  description = "Whether to use Lambda for hosting"
  type        = bool
  default     = false
}

variable "use_fargate" {
  description = "Whether to use Fargate for hosting"
  type        = bool
  default     = false
}

variable "thin_controller_regions" {
  description = "Comma-delimited list of regions to check/control"
  type        = string
  default     = ""
}

variable "vpc_id" {
  description = "VPC ID for Fargate deployment"
  type        = string
  default     = ""
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for Fargate deployment with NLB"
  type        = list(string)
  default     = []
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for Fargate tasks behind NLB"
  type        = list(string)
  default     = []
}

variable "ip_allow_list_inbound" {
  description = "List of IP CIDR blocks allowed to access the application"
  type        = list(string)
  default     = []
}

variable "managed_prefix_list_ids_allow_inbound" {
  description = "List of AWS VPC managed prefix list IDs allowed to access the application"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
