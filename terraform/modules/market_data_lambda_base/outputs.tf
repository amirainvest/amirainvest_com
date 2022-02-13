output "lambda-ecr-repository-url" {
  value = aws_ecr_repository.market_data_lambda.repository_url
}

output "lambda-ecr-image-id" {
  value = data.aws_ecr_image.lambda.id
}

output "lambda-image-uri" {
  value = "${aws_ecr_repository.market_data_lambda.repository_url}@${data.aws_ecr_image.lambda.id}"
}
