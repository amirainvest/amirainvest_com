resource "aws_cloudwatch_event_rule" "working_day_every_minute_cron" {
  description         = "${local.lambda_name} working_day_every_minute_cron"
  event_bus_name      = "default"
  is_enabled          = "false"
  name                = "${local.lambda_name}_working_day_every_minute_cron"
  schedule_expression = "cron(0/1 13-22 ? * MON-FRI *)"
}

resource "aws_lambda_permission" "allow_working_day_every_minute_cron_to_call_market_data_realtime_updates_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.market_data_realtime_updates_lambda.lambda-arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.working_day_every_minute_cron.arn
}
