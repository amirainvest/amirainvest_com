module "lambda_data_loader_producer" {
  source           = "./modules/lambda_eod_updates"
  region           = var.region
  environment      = var.environment
  private_subnets  = var.private_subnets
  vpc_id           = var.vpc_id
  lambda_image_uri = "${aws_ecr_repository.lambda.repository_url}@${data.aws_ecr_image.lambda.id}"
  project          = local.project
}

module "lambda_data_loader_consumer" {
  source           = "./modules/lambda_realtime_updates"
  lambda_name      = "${var.environment}-${local.project}-sqs-data-consumer"
  region           = var.region
  environment      = var.environment
  private_subnets  = var.private_subnets
  vpc_id           = var.vpc_id
  lambda_image_uri = "${aws_ecr_repository.lambda.repository_url}@${data.aws_ecr_image.lambda.id}"
  project          = local.project
}
