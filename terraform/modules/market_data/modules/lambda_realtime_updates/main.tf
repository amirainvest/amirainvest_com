module "market_data_realtime_updates_lambda" {
  source                                = "../../../lambda_base"
  region                                = var.region
  environment                           = var.environment
  private_subnets                       = var.private_subnets
  vpc_id                                = var.vpc_id
  project                               = local.project
  lambda_name                           = local.lambda_name
  lambda_image_uri                      = var.lambda_image_uri
  lambda_image_config_command           = ["market_data_amirainvest_com.lambdas.realtime_updates.app.handler"]
  lambda_reserved_concurrent_executions = 1
}
