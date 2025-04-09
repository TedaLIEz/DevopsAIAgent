module "azure_web_app" {
  source = "./modules/azure_web_app"

  # Resource Group Configuration
  resource_group_name = var.resource_group_name
  location            = var.location

  # Container Registry Configuration
  acr_name       = var.acr_name
  acr_sku        = var.acr_sku
  acr_image_name = var.acr_image_name

  # App Service Plan Configuration
  app_service_plan_name = var.app_service_plan_name
  app_service_sku       = var.app_service_sku

  # Web App Configuration
  web_app_name = var.web_app_name
}
