resource "aws_lambda_event_source_mapping" "sqs-to-consumer-lambda" {
  batch_size                         = "1"
  bisect_batch_on_function_error     = "false"
  enabled                            = "true"
  event_source_arn                   = var.read_sqs_arn
  function_name                      = module.lambda.lambda-arn
  maximum_batching_window_in_seconds = "0"
  tumbling_window_in_seconds         = "0"
}
