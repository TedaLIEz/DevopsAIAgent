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
  name     = "devopsAgentRg"
  location = "westus"
}


resource "azurerm_container_registry" "acr" {
  name                = "devopsAgentRegistry"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_service_plan" "asp" {
  name                = "devopsAgentServicePlan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "F1"
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "devopsAgentLaw"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}


resource "azurerm_linux_web_app" "app" {
  name                = "build-log-inspector"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.asp.id
  https_only          = true

  site_config {
    always_on = false

    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_image_name        = "devops_ai_agent:latest"
      docker_registry_password = azurerm_container_registry.acr.admin_password
      docker_registry_username = azurerm_container_registry.acr.admin_username
    }
  }

  app_settings = {
    DOCKER_ENABLE_CI = "true"
  }


}


resource "azurerm_kubernetes_cluster" "aks" {
  name                = "devops-agent-aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "devops-agent-aks"

  default_node_pool {
    name                = "default"
    node_count          = 1
    vm_size             = "Standard_B2s" # Most cost-effective VM size for dev/test
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "kubenet"
    network_policy = "calico"
  }

  sku_tier = "Free"

  monitor_metrics {}
}