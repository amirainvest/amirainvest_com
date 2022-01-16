variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr_block_base" {
  type    = string
  default = "10.0"
}
