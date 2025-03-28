# Container Registry
variable "acr_name" {
  type        = string
  description = "Name of Azure Container Registry"
  default     = "devopsAgentRegistry"
}

variable "acr_sku" {
  type        = string
  description = "SKU for Azure Container Registry"
  default     = "Basic"
}

variable "acr_image_name" {
  type        = string
  description = "Name of the image in the container registry"
  default     = "devops_ai_agent:latest"
}

# App Service Plan
variable "app_service_plan_name" {
  type        = string
  description = "Name of App Service Plan"
  default     = "devopsAgentServicePlan"
}

variable "app_service_sku" {
  type        = string
  description = "SKU for App Service Plan"
  default     = "F1"
}


# Web App
variable "web_app_name" {
  type        = string
  description = "Name of the web app"
  default     = "build-log-inspector"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
  default     = "devops-agent-rg"
}

variable "location" {
  type        = string
  description = "Location of the resource group"
  default     = "eastus"
}
