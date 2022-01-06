resource "aws_lambda_function" "prod-brokerage-data-sqs-consumer" {
  architectures = ["x86_64"]

  environment {
    variables = {
      ENVIRONMENT = "prod"
      PROJECT     = "brokerage"
    }
  }

  function_name                  = "prod-brokerage-data-sqs-consumer"
  image_uri                      = "${aws_ecr_repository.lambda.repository_url}@${data.aws_ecr_image.lambda.id}"
  memory_size                    = "256"
  package_type                   = "Image"
  reserved_concurrent_executions = "-1"
  role                           = "arn:aws:iam::903791206266:role/prod-lambda"
  source_code_hash               = "b03f25362d49e350017d0f2707efdf2e1d61ba2acbad1489ee704df50a863c95"

  tags = {
    env = "prod"
  }

  tags_all = {
    env = "prod"
  }

  timeout = "900"

  tracing_config {
    mode = "PassThrough"
  }

  vpc_config {
    security_group_ids = ["sg-05e6b9e1e61a849f4"]
    subnet_ids         = ["subnet-031bdf1a786694a68", "subnet-05a45c47337ce649e", "subnet-0bb4370ccc2df1e3e"]
  }
}
