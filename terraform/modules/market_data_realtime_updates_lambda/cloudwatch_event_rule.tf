resource "aws_cloudwatch_event_rule" "working_day_every_minute_cron" {
  description         = "test"
  event_bus_name      = "default"
  is_enabled          = "true"
  name                = "Test"
  schedule_expression = "cron(0 12 * * ? *)"
}
