output "grupo_recursos" {
  description = "Grupo de recursos de la aplicacion."
  value       = azurerm_resource_group.principal.name
}

output "region" {
  description = "Region de despliegue."
  value       = azurerm_resource_group.principal.location
}

output "vnet" {
  value = module.red.vnet_nombre
}

output "nsg_publica" {
  value = module.red.nsg_publica_nombre
}
