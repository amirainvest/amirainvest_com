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

module "market_data" {
  source      = "./modules/market_data"
  region          = var.region
  environment     = var.environment
  private_subnets = module.networking.private-subnets
  vpc_id          = module.networking.aws_vpc_public_private_id
}

module "data_imports" {
  source          = "./modules/data_imports"
  region          = var.region
  environment     = var.environment
  private_subnets = module.networking.private-subnets
  vpc_id          = module.networking.aws_vpc_public_private_id
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
  from = aws_sqs_queue.data-imports
  to   = module.data_imports.aws_sqs_queue.data-imports
}

moved {
  from = aws_sqs_queue.data-imports-deadletters
  to   = module.data_imports.aws_sqs_queue.data-imports-deadletters
}

moved {
  from = aws_sqs_queue.expedited-data-imports
  to   = module.data_imports.aws_sqs_queue.expedited-data-imports
}

moved {
  from = aws_sqs_queue.expedited-data-imports-deadletters
  to   = module.data_imports.aws_sqs_queue.expedited-data-imports-deadletters
}
