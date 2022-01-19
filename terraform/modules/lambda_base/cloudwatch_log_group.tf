resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.lambda_name}"
  retention_in_days = 120
  kms_key_id        = aws_kms_key.logs.arn
  tags = {
    env     = var.environment
    project = var.project
  }
}
