resource "aws_iam_policy" "write" {
  name = "${local.lambda_name}-lambda-sqs-write"
  path = "/service-role/"

  policy = <<POLICY
{
  "Statement": [
        {
        "Effect": "Allow",
        "Action": [
            "sqs:GetQueueAttributes",
            "sqs:SendMessage"
        ],
        "Resource": "*"
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}
