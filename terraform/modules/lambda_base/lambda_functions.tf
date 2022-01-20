resource "aws_lambda_function" "main" {
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
  reserved_concurrent_executions = var.lambda_reserved_concurrent_executions
  role                           = aws_iam_role.lambda.arn


  image_config {
    command = var.lambda_image_config_command
  }

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
