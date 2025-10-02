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

variable "cloudfront_geo_regions" {
  description = "Cloudfront geo whitelist regions, allowing source IPs"
  type        = list(string)
  default     = ["US", "AU"]
}

variable "thin_controller_regions" {
  description = "Comma-delimited list of regions to check/control"
  type        = string
  default     = ""
}
