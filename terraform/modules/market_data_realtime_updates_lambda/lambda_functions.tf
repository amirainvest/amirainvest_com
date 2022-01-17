resource "aws_lambda_function" "realtime_updates" {
  architectures = ["x86_64"]

  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT     = var.project
    }
  }

  function_name                  = local.lambda_name
  image_uri                      = "${aws_ecr_repository.lambda.repository_url}@${data.aws_ecr_image.lambda.id}"
  memory_size                    = "256"
  package_type                   = "Image"
  # TODO: Change limit to 1 after the quota is increased https://console.aws.amazon.com/servicequotas/home/services/lambda/quotas/L-B99A9384
  #   AWS is dumb and I hate the 50 default quota...
  reserved_concurrent_executions = "-1"
  role                           = aws_iam_role.lambda.arn

  tags = {
    env = var.environment
  }

  tags_all = {
    env = var.environment
  }

  timeout = "900"

  tracing_config {
    mode = "PassThrough"
  }

  vpc_config {
    security_group_ids = [aws_security_group.lambda.id]
    subnet_ids         = var.private_subnets
  }
}
