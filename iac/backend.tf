terraform {
  backend "s3" {
    bucket = "jayambar-terraform-backend"
    key = "project01"
    region = "us-east-1"
    profile = "default"
  }
}