resource "aws_iam_policy" "log-writing" {
  name = "${local.lambda_name}-lambda-log-writing"
  path = "/service-role/"

  policy = <<POLICY
{
  "Statement": [
    {
      "Action": "logs:CreateLogGroup",
      "Effect": "Allow",
      "Resource": "arn:aws:logs:${var.region}:903791206266:*"
    },
    {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow",
      "Resource": [
        "${aws_cloudwatch_log_group.lambda.arn}:*"
      ]
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}
