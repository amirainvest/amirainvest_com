resource "aws_iam_role" "lambda" {
  assume_role_policy = <<POLICY
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ],
  "Version": "2012-10-17"
}
POLICY

  description         = "${local.lambda_name}-lambda"
  managed_policy_arns = concat(var.lambda_managed_policy_arns, local.default_policies)

  max_session_duration = "3600"
  name                 = "${local.lambda_name}-lambda"
  path                 = "/"

  tags = {
    env = var.environment
  }

  tags_all = {
    env = var.environment
  }
}
