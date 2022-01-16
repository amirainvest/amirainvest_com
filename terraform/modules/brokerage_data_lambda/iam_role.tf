resource "aws_iam_role" "lambda" {
  assume_role_policy = <<POLICY
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ],
  "Version": "2012-10-17"
}
POLICY

  description = "Allows Lambda functions to call AWS services on your behalf."
  managed_policy_arns = [
    aws_iam_policy.lambda.arn,
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/AmazonSQSFullAccess",
    "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  ]

  max_session_duration = "3600"
  name                 = "${var.environment}-lambda"
  path                 = "/"

  tags = {
    env = var.environment
  }

  tags_all = {
    env = var.environment
  }
}
