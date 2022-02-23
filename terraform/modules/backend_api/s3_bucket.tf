resource "aws_s3_bucket" "amira-user-profile-photos" {
  bucket        = "${var.environment}-amira-user-profile-photos"
  force_destroy = "false"


  tags = {
    env     = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "amira-user-profile-photos" {
  bucket = aws_s3_bucket.amira-user-profile-photos.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

    bucket_key_enabled = "false"
  }
}

resource "aws_s3_bucket_request_payment_configuration" "amira-user-profile-photos" {
  bucket = aws_s3_bucket.amira-user-profile-photos.id
  payer  = "BucketOwner"
}

resource "aws_s3_bucket_versioning" "amira-user-profile-photos" {
  bucket = aws_s3_bucket.amira-user-profile-photos.id
  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Disabled"
  }
}

resource "aws_s3_bucket_acl" "amira-user-profile-photos" {
  bucket = aws_s3_bucket.amira-user-profile-photos.id
  acl    = "private"
}



resource "aws_s3_bucket" "amira-user-profile-photos-holding" {
  bucket        = "${var.environment}-amira-user-profile-photos-holding"
  force_destroy = "false"

  tags = {
    env     = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "amira-user-profile-photos-holding" {
  bucket = aws_s3_bucket.amira-user-profile-photos-holding.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

    bucket_key_enabled = "false"
  }
}

resource "aws_s3_bucket_request_payment_configuration" "amira-user-profile-photos-holding" {
  bucket = aws_s3_bucket.amira-user-profile-photos-holding.id
  payer  = "BucketOwner"
}

resource "aws_s3_bucket_versioning" "amira-user-profile-photos-holding" {
  bucket = aws_s3_bucket.amira-user-profile-photos-holding.id
  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Disabled"
  }
}

resource "aws_s3_bucket_acl" "amira-user-profile-photos-holding" {
  bucket = aws_s3_bucket.amira-user-profile-photos-holding.id
  acl    = "private"
}



resource "aws_s3_bucket" "amira-post-photos" {
  bucket        = "${var.environment}-amira-post-photos"
  force_destroy = "false"

  tags = {
    env     = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "amira-post-photos" {
  bucket = aws_s3_bucket.amira-post-photos.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

    bucket_key_enabled = "false"
  }
}

resource "aws_s3_bucket_request_payment_configuration" "amira-post-photos" {
  bucket = aws_s3_bucket.amira-post-photos.id
  payer  = "BucketOwner"
}

resource "aws_s3_bucket_versioning" "amira-post-photos" {
  bucket = aws_s3_bucket.amira-post-photos.id
  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Disabled"
  }
}

resource "aws_s3_bucket_acl" "amira-post-photos" {
  bucket = aws_s3_bucket.amira-post-photos.id
  acl    = "private"
}



resource "aws_s3_bucket" "amira-post-photos-holding" {
  bucket        = "${var.environment}-amira-post-photos-holding"
  force_destroy = "false"

  tags = {
    env     = var.environment
    project = "backend_api"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "amira-post-photos-holding" {
  bucket = aws_s3_bucket.amira-post-photos-holding.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

    bucket_key_enabled = "false"
  }
}

resource "aws_s3_bucket_request_payment_configuration" "amira-post-photos-holding" {
  bucket = aws_s3_bucket.amira-post-photos-holding.id
  payer  = "BucketOwner"
}

resource "aws_s3_bucket_versioning" "amira-post-photos-holding" {
  bucket = aws_s3_bucket.amira-post-photos-holding.id
  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Disabled"
  }
}

resource "aws_s3_bucket_acl" "amira-post-photos-holding" {
  bucket = aws_s3_bucket.amira-post-photos-holding.id
  acl    = "private"
}
