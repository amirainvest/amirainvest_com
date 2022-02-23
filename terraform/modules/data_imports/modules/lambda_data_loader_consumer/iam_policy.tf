resource "aws_iam_policy" "sqs_read_delete" {
  name = "${var.lambda_name}-lambda-sqs-read-delete"
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
