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
