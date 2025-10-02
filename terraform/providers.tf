terraform {

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.46.0"
    }
  }
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

# CloudFront WAF must be in us-east-1
provider "aws" {
  alias   = "us-east-1"
  profile = var.aws_profile
  region  = "us-east-1"
}
