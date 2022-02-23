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

variable "lambda_image_uri" {
  type = string
}

variable "project" {
  type = string
}

locals {
  lambda_name = "${var.environment}-${var.project}-sqs-data-producer"
}
