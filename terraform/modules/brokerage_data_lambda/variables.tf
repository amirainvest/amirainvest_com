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
  type    = string
  default = "brokerage"
}

variable "vpc_id" {
  type = string
}
