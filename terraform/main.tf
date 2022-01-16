module "backend_api" {
  source      = "./modules/backend_api"
  region      = var.region
  environment = var.environment
}

module "brokerage_data_lambda" {
  source      = "./modules/brokerage_data_lambda"
  region      = var.region
  environment = var.environment
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

