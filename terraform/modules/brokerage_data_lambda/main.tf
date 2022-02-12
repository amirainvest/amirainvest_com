module "brokerage_data_lambda" {
  source                      = "../lambda_base"
  region                      = var.region
  environment                 = var.environment
  private_subnets             = var.private_subnets
  vpc_id                      = var.vpc_id
  project                     = local.project
  lambda_managed_policy_arns  = [aws_iam_policy.sqs_read_write.arn, aws_iam_policy.dynamo_read_write.arn]
  lambda_name                 = local.lambda_name
  lambda_image_config_command = ["brokerage_amirainvest_com.lambdas.app.handler"]
}
