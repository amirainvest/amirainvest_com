module "networking" {
  source      = "../networking"
  region      = var.region
  environment = var.environment
}
