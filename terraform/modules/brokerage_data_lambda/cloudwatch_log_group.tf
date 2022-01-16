resource "aws_cloudwatch_log_group" "lambda" {
  name = "/aws/lambda/${var.environment}-${var.project}-data-sqs-consumer"
  retention_in_days = 120
  kms_key_id = aws_kms_key.logs
  tags = {
    env = var.environment
    project = var.project
  }
}
