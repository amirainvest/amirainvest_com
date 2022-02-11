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
  project = "brokerage"
  lambda_name = "${var.environment}-brokerage-data-sqs-consumer"
}
