resource "aws_lambda_function" "brokerage-data-sqs-consumer" {
  architectures = ["x86_64"]

  environment {
    variables = {
      ENVIRONMENT = var.environment
      PROJECT     = var.project
    }
  }

  function_name                  = "${var.environment}-brokerage-data-sqs-consumer"
  image_uri                      = "${aws_ecr_repository.lambda.repository_url}@${data.aws_ecr_image.lambda.id}"
  memory_size                    = "256"
  package_type                   = "Image"
  reserved_concurrent_executions = "-1"
  role                           = "arn:aws:iam::903791206266:role/${var.environment}-lambda"

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
