module "brokerage_data_lambda" {
  source                      = "../lambda_base"
  region                      = var.region
  environment                 = var.environment
  private_subnets             = var.private_subnets
  vpc_id                      = var.vpc_id
  project                     = local.project
  lambda_name                 = "${var.environment}-brokerage-data-sqs-consumer"
  lambda_image_config_command = ["brokerage_amirainvest_com.lambdas.app.handler"]
}

moved {
  from = aws_cloudwatch_log_group.lambda
  to   = module.brokerage_data_lambda.aws_cloudwatch_log_group.lambda
}

moved {
  from = aws_ecr_repository.lambda
  to   = module.brokerage_data_lambda.aws_ecr_repository.lambda
}

moved {
  from = aws_iam_policy.lambda
  to   = module.brokerage_data_lambda.aws_iam_policy.log-writing
}

moved {
  from = aws_iam_role.lambda
  to   = module.brokerage_data_lambda.aws_iam_role.lambda
}

moved {
  from = aws_kms_key.logs
  to   = module.brokerage_data_lambda.aws_kms_key.logs
}

moved {
  from = aws_lambda_function.brokerage-data-sqs-consumer
  to   = module.brokerage_data_lambda.aws_lambda_function.main
}

moved {
  from = aws_security_group.lambda
  to   = module.brokerage_data_lambda.aws_security_group.lambda
}
