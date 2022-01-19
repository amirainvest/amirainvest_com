resource "aws_cloudwatch_event_rule" "working_day_every_minute_cron" {
  description         = "${local.lambda_name} working_day_every_minute_cron"
  event_bus_name      = "default"
  is_enabled          = "true"
  name                = "${local.lambda_name}_working_day_every_minute_cron"
  schedule_expression = "cron(0 12 * * ? *)"
}
