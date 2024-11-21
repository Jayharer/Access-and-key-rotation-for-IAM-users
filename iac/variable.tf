
variable "AWS_REGION" {
  type    = string
  default = "us-east-1"
}

variable "lambda_key_rotation" {
  type    = string
  default = "sam-app-KeyRotationFunction-WUxxCiiagHhX"
}

variable "lambda_console_access" {
  type    = string
  default = "sam-app-ConsoleAccessFunction-xNLiHLMIbhEG"
}
