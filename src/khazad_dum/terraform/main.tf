# One AWS provider + one module instance per supported region. Terraform cannot
# select a provider dynamically from a for_each value, so each region a server
# can target needs a static provider alias and module block below. The CLI
# validates server regions against this same list.

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us_east_2"
  region = "us-east-2"
}

provider "aws" {
  alias  = "us_west_2"
  region = "us-west-2"
}

provider "aws" {
  alias  = "eu_west_1"
  region = "eu-west-1"
}

provider "aws" {
  alias  = "eu_west_2"
  region = "eu-west-2"
}

provider "aws" {
  alias  = "eu_central_1"
  region = "eu-central-1"
}

module "us_east_1" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = { for k, s in var.servers : k => s if s.region == "us-east-1" }
  providers = {
    aws = aws.us_east_1
  }
}

module "us_east_2" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = { for k, s in var.servers : k => s if s.region == "us-east-2" }
  providers = {
    aws = aws.us_east_2
  }
}

module "us_west_2" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = { for k, s in var.servers : k => s if s.region == "us-west-2" }
  providers = {
    aws = aws.us_west_2
  }
}

module "eu_west_1" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = { for k, s in var.servers : k => s if s.region == "eu-west-1" }
  providers = {
    aws = aws.eu_west_1
  }
}

module "eu_west_2" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = { for k, s in var.servers : k => s if s.region == "eu-west-2" }
  providers = {
    aws = aws.eu_west_2
  }
}

module "eu_central_1" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = { for k, s in var.servers : k => s if s.region == "eu-central-1" }
  providers = {
    aws = aws.eu_central_1
  }
}
