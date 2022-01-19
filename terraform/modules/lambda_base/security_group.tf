resource "aws_security_group" "lambda" {
  description = "SG ${local.lambda_name}"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  name   = "${local.lambda_name}-lambda-SG"
  vpc_id = var.vpc_id
}
