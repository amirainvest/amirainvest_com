variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "private_subnets" {
  type = list(string)
}

variable "vpc_id" {
  type = string
}

locals {
  project     = "market_data"
  lambda_name = "${var.environment}-market-data-realtime-updates"
}
