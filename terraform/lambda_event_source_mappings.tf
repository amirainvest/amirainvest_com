resource "aws_lambda_event_source_mapping" "sqs_to_test_stuff_and_things" {
  batch_size                         = "10"
  bisect_batch_on_function_error     = "false"
  enabled                            = "true"
  event_source_arn                   = "arn:aws:sqs:us-east-1:903791206266:prod-brokerage-data"
  function_name                      = aws_lambda_function.testing_stuff_and_things.arn
  maximum_batching_window_in_seconds = "0"
  maximum_record_age_in_seconds      = "-1"
  maximum_retry_attempts             = "3"
  parallelization_factor             = "10"
  tumbling_window_in_seconds         = "0"
}
