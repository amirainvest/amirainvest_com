//resource "aws_lambda_event_source_mapping" "eventbridge-lambda" {
//  batch_size                         = "10"
//  bisect_batch_on_function_error     = "false"
//  enabled                            = "true"
//  event_source_arn                   =
//  function_name                      = aws_lambda_function.brokerage-data-sqs-consumer.arn
//  maximum_batching_window_in_seconds = "0"
//  tumbling_window_in_seconds         = "0"
//}
