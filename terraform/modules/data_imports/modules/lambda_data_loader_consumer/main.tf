module "lambda" {
  source                      = "../../../lambda_base"
  region                      = var.region
  environment                 = var.environment
  private_subnets             = var.private_subnets
  vpc_id                      = var.vpc_id
  project                     = var.project
  lambda_managed_policy_arns  = [aws_iam_policy.sqs_read_delete.arn]
  lambda_name                 = var.lambda_name
  lambda_image_uri            = var.lambda_image_uri
  lambda_image_config_command = ["${var.project}_amirainvest_com.lambdas.data_loader_consumer.app.handler"]
}
