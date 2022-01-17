variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "private_subnets" {
  type = list(string)
}

variable "project" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "lambda_name" {
  type    = string
  default = ""
}


locals {
  lambda_name = var.lambda_name != "" ? var.lambda_name : "${var.environment}-${var.project}"
}
