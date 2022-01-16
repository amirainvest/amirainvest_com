resource "aws_iam_policy" "lambda" {
  name = "AWSLambdaBasicExecutionRole-87993df2-cbce-4e40-8d00-031a459187c8"
  path = "/service-role/"

  policy = <<POLICY
{
  "Statement": [
    {
      "Action": "logs:CreateLogGroup",
      "Effect": "Allow",
      "Resource": "arn:aws:logs:us-east-1:903791206266:*"
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
