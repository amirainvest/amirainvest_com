module "backend_api" {
  source      = "./modules/backend_api"
  region      = var.region
  environment = var.environment
  private_subnets = [
    module.networking.subnet-private-1-id,
    module.networking.subnet-private-2-id,
    module.networking.subnet-private-3-id,
  ]
  vpc_id = module.networking.aws_vpc_public_private_id
}
module "brokerage_data_lambda_base" {
  source      = "./modules/brokerage_data_lambda_base"
  region      = var.region
  environment = var.environment
}

module "brokerage_data_lambda" {
  source = "./modules/brokerage_data_lambda"

  lambda_image_uri = module.brokerage_data_lambda_base.lambda-image-uri
  region           = var.region
  environment      = var.environment
  private_subnets = [
    module.networking.subnet-private-1-id,
    module.networking.subnet-private-2-id,
    module.networking.subnet-private-3-id,
  ]
  vpc_id = module.networking.aws_vpc_public_private_id
}

module "market_data_lambda_base" {
  source      = "./modules/market_data_lambda_base"
  region      = var.region
  environment = var.environment
}

module "market_data_realtime_updates_lambda" {
  source = "./modules/market_data_realtime_updates_lambda"

  lambda_image_uri = module.market_data_lambda_base.lambda-image-uri
  region           = var.region
  environment      = var.environment
  private_subnets = [
    module.networking.subnet-private-1-id,
    module.networking.subnet-private-2-id,
    module.networking.subnet-private-3-id,
  ]
  vpc_id = module.networking.aws_vpc_public_private_id
}

module "market_data_eod_updates_lambda" {
  source           = "./modules/market_data_eod_updates_lambda"
  lambda_image_uri = module.market_data_lambda_base.lambda-image-uri

  region      = var.region
  environment = var.environment
  private_subnets = [
    module.networking.subnet-private-1-id,
    module.networking.subnet-private-2-id,
    module.networking.subnet-private-3-id,
  ]
  vpc_id = module.networking.aws_vpc_public_private_id
}


module "networking" {
  source      = "./modules/networking"
  region      = var.region
  environment = var.environment
}

terraform {
  cloud {
    organization = "Amirainvest"
    workspaces {
      name = "Production"
    }
  }
}

moved {
  from = module.market_data_realtime_updates_lambda.module.market_data_realtime_updates_lambda.aws_ecr_repository.lambda
  to   = module.market_data_lambda_base.aws_ecr_repository.market_data_lambda
}

moved {
  from = module.brokerage_data_lambda.module.brokerage_data_lambda.aws_ecr_repository.lambda
  to   = module.brokerage_data_lambda_base.aws_ecr_repository.brokerage_data_lambda
}

