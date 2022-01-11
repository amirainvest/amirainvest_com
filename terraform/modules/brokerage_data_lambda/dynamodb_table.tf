resource "aws_dynamodb_table" "brokerage_users" {
  attribute {
    name = "user_id"
    type = "S"
  }

  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  name         = "brokerage_users"

  point_in_time_recovery {
    enabled = "false"
  }

  stream_enabled = "false"
  table_class    = "STANDARD"

  tags = {
    env     = "prod"
    project = "brokerage"
  }

  tags_all = {
    env     = "prod"
    project = "brokerage"
  }

  read_capacity  = "0"
  write_capacity = "0"

  lifecycle {
    ignore_changes = [
      read_capacity,
      write_capacity,
    ]
  }
}
