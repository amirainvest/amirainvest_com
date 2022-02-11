resource "aws_iam_policy" "sqs_read_write" {
  name = "${local.lambda_name}-lambda-sqs-read-write"
  path = "/service-role/"

  policy = <<POLICY
{
  "Statement": [
        {
        "Effect": "Allow",
        "Action": [
            "sqs:ReceiveMessage",
            "sqs:DeleteMessage",
            "sqs:GetQueueAttributes"
        ],
        "Resource": "*"
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}


resource "aws_iam_policy" "dynamo_read_write" {
  name = "${local.lambda_name}-lambda-dynamo-read-write"
  path = "/service-role/"

  policy = <<POLICY
{
  "Statement": [
            {
            "Action": [
                "dynamodb:*"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
  ]
  "Version": "2012-10-17"
}
POLICY
}
