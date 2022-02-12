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
variable "lambda_managed_policy_arns" {
  type    = list(string)
  default = []
}

variable "lambda_reserved_concurrent_executions" {
  type    = number
  default = -1
}

variable "lambda_image_uri" {
  type = string
}

variable "lambda_image_config_command" {
  type = list(string)
}


locals {
  lambda_name = var.lambda_name != "" ? var.lambda_name : "${var.environment}-${var.project}"
  default_policies = [
    aws_iam_policy.log-writing.arn,
    "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  ]
}
