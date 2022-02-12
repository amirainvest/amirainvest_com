resource "aws_cloudwatch_event_target" "working_day_market_close_cron" {
  arn  = module.market_data_eod_updates_lambda.lambda-arn
  rule = aws_cloudwatch_event_rule.working_day_market_close.name
}
