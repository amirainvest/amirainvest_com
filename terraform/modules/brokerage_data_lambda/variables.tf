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
