module "lambda_data_loader_producer" {
  source           = "./modules/lambda_data_loader_producer"
  region           = var.region
  environment      = var.environment
  private_subnets  = var.private_subnets
  vpc_id           = var.vpc_id
  lambda_image_uri = aws_ecr_repository.lambda.repository_url
  project          = local.project
}

module "lambda_data_loader_consumer" {
  source           = "./modules/lambda_data_loader_consumer"
  lambda_name      = "${var.environment}-${local.project}-sqs-data-consumer"
  region           = var.region
  environment      = var.environment
  private_subnets  = var.private_subnets
  vpc_id           = var.vpc_id
  lambda_image_uri = aws_ecr_repository.lambda.repository_url
  project          = local.project
  read_sqs_arn     = aws_sqs_queue.data-imports.arn
}

module "lambda_data_loader_consumer_expedited" {
  source           = "./modules/lambda_data_loader_consumer"
  lambda_name      = "${var.environment}-${local.project}-sqs-data-consumer-expedited"
  region           = var.region
  environment      = var.environment
  private_subnets  = var.private_subnets
  vpc_id           = var.vpc_id
  lambda_image_uri = aws_ecr_repository.lambda.repository_url
  project          = local.project
  read_sqs_arn     = aws_sqs_queue.expedited-data-imports.arn
}
