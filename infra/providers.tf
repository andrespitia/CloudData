terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "H3-CC-TT-terraform"
    storage_account_name = "cloudterraformandrespi"
    container_name       = "tfstate"
    key                  = "clouddata.tfstate"
  }
}

provider "azurerm" {
  features {}

  resource_provider_registrations = "none"
}