resource "aws_cloudwatch_event_rule" "working_day_market_close" {
  description         = "${local.lambda_name} working_day_market_close"
  event_bus_name      = "default"
  is_enabled          = "true"
  name                = "${local.lambda_name}_working_day_market_close"
  schedule_expression = "cron(0 50 16 ? * MON-FRI *)"
}

resource "aws_lambda_permission" "allow_working_day_market_close_cron_to_call_market_data_eod_updates_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.market_data_eod_updates_lambda.lambda-arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.working_day_market_close.arn
}
