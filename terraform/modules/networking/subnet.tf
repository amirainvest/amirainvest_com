resource "aws_subnet" "private-1" {
  assign_ipv6_address_on_creation = "false"
  cidr_block                      = "${var.vpc_cidr_block_base}.1.0/24"
  map_customer_owned_ip_on_launch = "false"
  map_public_ip_on_launch         = "false"

  tags = {
    env  = var.environment
    Name = "Private subnet"
  }

  tags_all = {
    env  = var.environment
    Name = "Private subnet"
  }

  vpc_id = aws_vpc.public-private
}

resource "aws_subnet" "private-2" {
  assign_ipv6_address_on_creation = "false"
  cidr_block                      = "${var.vpc_cidr_block_base}.2.0/24"
  map_customer_owned_ip_on_launch = "false"
  map_public_ip_on_launch         = "false"

  tags = {
    env  = var.environment
    Name = "Private 2 subnet"
  }

  tags_all = {
    env  = var.environment
    Name = "Private 2 subnet"
  }

  vpc_id = aws_vpc.public-private
}

resource "aws_subnet" "private-3" {
  assign_ipv6_address_on_creation = "false"
  cidr_block                      = "${var.vpc_cidr_block_base}.3.0/24"
  map_customer_owned_ip_on_launch = "false"
  map_public_ip_on_launch         = "false"

  tags = {
    env  = var.environment
    Name = "Private 3 subnet"
  }

  tags_all = {
    env  = var.environment
    Name = "Private 3 subnet"
  }

  vpc_id = aws_vpc.public-private
}
resource "aws_subnet" "public-1" {
  assign_ipv6_address_on_creation = "false"
  cidr_block                      = "${var.vpc_cidr_block_base}.0.0/24"
  map_customer_owned_ip_on_launch = "false"
  map_public_ip_on_launch         = "false"

  tags = {
    env  = var.environment
    Name = "Public subnet"
  }

  tags_all = {
    env  = var.environment
    Name = "Public subnet"
  }

  vpc_id = aws_vpc.public-private
}

resource "aws_subnet" "public-2" {
  assign_ipv6_address_on_creation = "false"
  cidr_block                      = "${var.vpc_cidr_block_base}.10.0/24"
  map_customer_owned_ip_on_launch = "false"
  map_public_ip_on_launch         = "false"

  tags = {
    env  = var.environment
    Name = "Public 2 subnet"
  }

  tags_all = {
    env  = var.environment
    Name = "Public 2 subnet"
  }

  vpc_id = aws_vpc.public-private
}

resource "aws_subnet" "public-3" {
  assign_ipv6_address_on_creation = "false"
  cidr_block                      = "${var.vpc_cidr_block_base}.11.0/24"
  map_customer_owned_ip_on_launch = "false"
  map_public_ip_on_launch         = "false"

  tags = {
    env  = var.environment
    Name = "Public 3 subnet"
  }

  tags_all = {
    env  = var.environment
    Name = "Public 3 subnet"
  }

  vpc_id = aws_vpc.public-private
}

