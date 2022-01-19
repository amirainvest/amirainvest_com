module "market_data_realtime_updates_lambda" {
  source                      = "../lambda_base"
  region                      = var.region
  environment                 = var.environment
  private_subnets             = var.private_subnets
  vpc_id                      = var.vpc_id
  project                     = "market_data"
  lambda_name                 = "${var.environment}-market-data-realtime-updates"
  lambda_image_config_command = ["market_data_amirainvest_com.lambdas.app.handler"]
}
