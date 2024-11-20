
variable "AWS_REGION" {
  type    = string
  default = "us-east-1"
}

variable "lambda_key_rotation" {
  type    = string
  default = "access_secret_key_rotation"
}

variable "lambda_aws_console_access" {
  type    = string
  default = "disable_console_login"
}
