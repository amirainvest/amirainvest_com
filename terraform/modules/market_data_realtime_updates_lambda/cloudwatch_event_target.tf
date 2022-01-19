resource "aws_cloudwatch_event_target" "working_day_every_minute_cron" {
  arn       = module.market_data_realtime_updates_lambda.lambda-arn
  rule      = aws_cloudwatch_event_rule.working_day_every_minute_cron.name
}
