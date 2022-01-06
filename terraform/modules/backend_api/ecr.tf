resource "aws_ecr_repository" "backend_amirainvest_com" {
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = "arn:aws:kms:${var.region}:903791206266:key/d1f57297-6d72-455a-8839-ce498e9162db"
  }

  image_scanning_configuration {
    scan_on_push = "true"
  }

  image_tag_mutability = "MUTABLE"
  name                 = "amirainvest_com/backend_amirainvest_com"
}


data "aws_ecr_image" "backend_amirainvest_com" {
  repository_name = aws_ecr_repository.backend_amirainvest_com.name
  image_tag = "latest"
}


