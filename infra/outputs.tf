output "grupo_recursos" {
  description = "Grupo de recursos de la aplicacion."
  value       = azurerm_resource_group.principal.name
}

output "region" {
  description = "Region de despliegue."
  value       = azurerm_resource_group.principal.location
}