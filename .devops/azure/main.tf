terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.112.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "tfstate"
    storage_account_name = "tfstate3811"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}



resource "azurerm_log_analytics_workspace" "law" {
  name                = var.log_analytics_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.log_analytics_sku
  retention_in_days   = var.log_retention_days
}


resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.acr_sku
  admin_enabled       = true
}

resource "azurerm_service_plan" "asp" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = var.app_service_sku
}

resource "azurerm_linux_web_app" "app" {
  name                = var.web_app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.asp.id
  https_only          = true

  site_config {
    always_on = false

    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_image_name        = var.acr_image_name
      docker_registry_password = azurerm_container_registry.acr.admin_password
      docker_registry_username = azurerm_container_registry.acr.admin_username
    }
  }

  app_settings = {
    DOCKER_ENABLE_CI = "true"
  }


}




