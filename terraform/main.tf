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

module "brokerage_data_lambda" {
  source      = "./modules/brokerage_data_lambda"
  region      = var.region
  environment = var.environment
  private_subnets = [
    module.networking.subnet-private-1-id,
    module.networking.subnet-private-2-id,
    module.networking.subnet-private-3-id,
  ]
  vpc_id  = module.networking.aws_vpc_public_private_id
}

module "market_data_realtime_updates_lambda" {
  source = "./modules/market_data_realtime_updates_lambda"

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

