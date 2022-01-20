resource "aws_vpc" "public-private" {
  assign_generated_ipv6_cidr_block = "false"
  cidr_block                       = "${var.vpc_cidr_block_base}.0.0/16"
  enable_classiclink               = "false"
  enable_classiclink_dns_support   = "false"
  enable_dns_hostnames             = "true"
  enable_dns_support               = "true"
  instance_tenancy                 = "default"

  tags = {
    Name = "Public-private"
    env  = var.environment
  }

  tags_all = {
    Name = "Public-private"
    env  = var.environment
  }
}
