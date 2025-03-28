# Resource Group
variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
  default     = "devopsAgentRg"
}

variable "location" {
  type        = string
  description = "Azure region for resources"
  default     = "westus"
}

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



# Log Analytics
variable "log_analytics_name" {
  type        = string
  description = "Name of Log Analytics Workspace"
  default     = "devopsAgentLaw"
}

variable "log_retention_days" {
  type        = number
  description = "Number of days to retain logs"
  default     = 30
}

variable "log_analytics_sku" {
  type        = string
  description = "SKU for Log Analytics Workspace"
  default     = "PerGB2018"
}

# AKS Cluster
variable "aks_cluster_name" {
  type        = string
  description = "Name of AKS cluster"
  default     = "devops-agent-aks"
}

variable "aks_node_count" {
  type        = number
  description = "Number of nodes in AKS cluster"
  default     = 1
}

variable "aks_vm_size" {
  type        = string
  description = "VM size for AKS nodes"
  default     = "Standard_B2s"
}



variable "metric_labels_allowlist" {
  default = null
}

variable "metric_annotations_allowlist" {
  default = null
}

variable "monitor_workspace_name" {
  default = "devops-agent-amw"
}

variable "grafana_name" {
  default = "devops-agent-grafana"
}

variable "grafana_version" {
  default = "10"
}

variable "streams" {
  default = ["Microsoft-ContainerLog", "Microsoft-ContainerLogV2", "Microsoft-KubeEvents", "Microsoft-KubePodInventory", "Microsoft-KubeNodeInventory", "Microsoft-KubePVInventory", "Microsoft-KubeServices", "Microsoft-KubeMonAgentEvents", "Microsoft-InsightsMetrics", "Microsoft-ContainerInventory", "Microsoft-ContainerNodeInventory", "Microsoft-Perf"]
}


variable "data_collection_interval" {
  default = "1m"
}

variable "namespace_filtering_mode_for_data_collection" {
  default = "Off"
}

variable "namespaces_for_data_collection" {
  default = ["kube-system", "gatekeeper-system", "azure-arc"]
}

variable "enableContainerLogV2" {
  default = true
}
