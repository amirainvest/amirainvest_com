resource "aws_lambda_event_source_mapping" "sqs-to-brokerage-data-sqs-consumer-lambda" {
  batch_size                         = "10"
  bisect_batch_on_function_error     = "false"
  enabled                            = "true"
  event_source_arn                   = aws_sqs_queue.brokerage-data.arn
  function_name                      = module.brokerage_data_lambda.lambda-arn
  maximum_batching_window_in_seconds = "0"
  tumbling_window_in_seconds         = "0"
}
