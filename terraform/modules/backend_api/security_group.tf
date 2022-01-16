resource "aws_security_group" "api-public-service" {
  description = "Security group for the api-public ECS service "

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    from_port       = "5000"
    protocol        = "tcp"
    security_groups = ["sg-025dfb942e00cd15c"]
    self            = "false"
    to_port         = "5000"
  }

  ingress {
    from_port       = "80"
    protocol        = "tcp"
    security_groups = ["sg-025dfb942e00cd15c"]
    self            = "false"
    to_port         = "80"
  }

  name   = "${var.environment}-api-public-service-SG"
  vpc_id = var.vpc_id
}
