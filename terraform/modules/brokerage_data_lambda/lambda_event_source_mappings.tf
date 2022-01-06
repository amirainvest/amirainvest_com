resource "aws_lambda_event_source_mapping" "sqs-to-brokerage-data-sqs-consumer-lambda" {
  batch_size                         = "10"
  bisect_batch_on_function_error     = "false"
  enabled                            = "true"
  event_source_arn                   = "arn:aws:sqs:${var.region}:903791206266:${var.environment}-brokerage-data"
  function_name                      = aws_lambda_function.brokerage-data-sqs-consumer.arn
  maximum_batching_window_in_seconds = "0"
  tumbling_window_in_seconds         = "0"
}
