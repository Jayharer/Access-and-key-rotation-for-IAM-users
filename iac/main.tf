# terraform config
terraform {
  required_version = ">= 1.0.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.AWS_REGION
  profile = "default"
}

