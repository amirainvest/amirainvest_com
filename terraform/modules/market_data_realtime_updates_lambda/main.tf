module "market_data_realtime_updates_lambda" {
  source                      = "../lambda_base"
  region                      = var.region
  environment                 = var.environment
  private_subnets             = var.private_subnets
  vpc_id                      = var.vpc_id
  project                     = local.project
  lambda_name                 = local.lambda_name
  lambda_image_config_command = ["market_data_amirainvest_com.lambdas.app.handler"]
}

moved {
  from = aws_cloudwatch_log_group.lambda
  to   = module.market_data_realtime_updates_lambda.aws_cloudwatch_log_group.lambda
}

moved {
  from = aws_ecr_repository.lambda
  to   = module.market_data_realtime_updates_lambda.aws_ecr_repository.lambda
}

moved {
  from = aws_iam_policy.log-writing
  to   = module.market_data_realtime_updates_lambda.aws_iam_policy.log-writing
}

moved {
  from = aws_iam_role.lambda
  to   = module.market_data_realtime_updates_lambda.aws_iam_role.lambda
}

moved {
  from = aws_kms_key.logs
  to   = module.market_data_realtime_updates_lambda.aws_kms_key.logs
}

moved {
  from = aws_lambda_function.realtime_updates
  to   = module.market_data_realtime_updates_lambda.aws_lambda_function.main
}

moved {
  from = aws_security_group.lambda
  to   = module.market_data_realtime_updates_lambda.aws_security_group.lambda
}
