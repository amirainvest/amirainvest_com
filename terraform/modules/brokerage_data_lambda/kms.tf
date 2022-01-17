resource "aws_kms_key" "logs" {
  description = "KMS key for ${var.environment}-${var.project} lambda logs"
  key_usage = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  policy = <<EOT
{
 "Version": "2012-10-17",
    "Id": "key-default-1",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::903791206266:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "logs.${var.region}.amazonaws.com"
            },
            "Action": [
                "kms:Encrypt*",
                "kms:Decrypt*",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:Describe*"
            ],
            "Resource": "*",
            "Condition": {
                "ArnLike": {
                    "kms:EncryptionContext:aws:logs:arn": "arn:aws:logs:${var.region}:903791206266:*"
                }
            }
        }
    ]
}

EOT
  deletion_window_in_days = 30
  is_enabled = "true"
  enable_key_rotation = "false"
  multi_region = "false"
  tags = {
    env = var.environment
    project = var.project
  }
}

// data "aws_iam_policy_document" "logs" {
//
//}
