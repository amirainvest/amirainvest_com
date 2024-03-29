resource "aws_sqs_queue" "photo-processing" {
  content_based_deduplication       = "false"
  delay_seconds                     = "0"
  fifo_queue                        = "false"
  kms_data_key_reuse_period_seconds = "300"
  max_message_size                  = "262144"
  message_retention_seconds         = "345600"
  name                              = "${var.environment}-photo-processing"

  policy = <<POLICY
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::903791206266:root"
      },
      "Resource": "arn:aws:sqs:us-east-1:903791206266:${var.environment}-photo-processing",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2008-10-17"
}
POLICY

  receive_wait_time_seconds = "0"
  redrive_policy = jsonencode(
    {
      "deadLetterTargetArn" : aws_sqs_queue.photo-processing-deadletter.arn,
      "maxReceiveCount" : 10
    }
  )
  sqs_managed_sse_enabled    = "false"
  visibility_timeout_seconds = "901"
  tags = {
    env = var.environment
  }
}


resource "aws_sqs_queue" "photo-processing-deadletter" {
  content_based_deduplication       = "false"
  delay_seconds                     = "0"
  fifo_queue                        = "false"
  kms_data_key_reuse_period_seconds = "300"
  max_message_size                  = "262144"
  message_retention_seconds         = "345600"
  name                              = "${var.environment}-photo-processing-deadletter"

  policy = <<POLICY
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::903791206266:root"
      },
      "Resource": "arn:aws:sqs:us-east-1:903791206266:${var.environment}-photo-processing-deadletter",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2008-10-17"
}
POLICY

  receive_wait_time_seconds  = "0"
  sqs_managed_sse_enabled    = "false"
  visibility_timeout_seconds = "30"
  tags = {
    env = var.environment
  }
}
