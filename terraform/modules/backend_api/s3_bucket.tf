resource "aws_s3_bucket" "amira-user-profile-photos" {
  bucket        = "${var.environment}-amira-user-profile-photos"
  force_destroy = "false"
  request_payer = "BucketOwner"
  acl           = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }

      bucket_key_enabled = "false"
    }
  }

  versioning {
    enabled    = "true"
    mfa_delete = "false"
  }

  tags = {
    env = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket" "amira-user-profile-photos-holding" {
  bucket        = "${var.environment}-amira-user-profile-photos-holding"
  force_destroy = "false"
  request_payer = "BucketOwner"
  acl           = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }

      bucket_key_enabled = "false"
    }
  }

  versioning {
    enabled    = "true"
    mfa_delete = "false"
  }

  tags = {
    env = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket" "amira-post-photos" {
  bucket        = "${var.environment}-amira-post-photos"
  force_destroy = "false"
  request_payer = "BucketOwner"
  acl           = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }

      bucket_key_enabled = "false"
    }
  }

  versioning {
    enabled    = "true"
    mfa_delete = "false"
  }

  tags = {
    env = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket" "amira-post-photos-holding" {
  bucket        = "${var.environment}-amira-post-photos-holding"
  force_destroy = "false"
  request_payer = "BucketOwner"
  acl           = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }

      bucket_key_enabled = "false"
    }
  }

  versioning {
    enabled    = "true"
    mfa_delete = "false"
  }

  tags = {
    env = var.environment
    project = "backend_api"
  }
}
