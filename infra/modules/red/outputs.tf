output "vnet_id" {
  description = "ID de la red virtual"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_nombre" {
  value = azurerm_virtual_network.vnet.name
}

output "subred_publica_id" {
  description = "Subred donde ira la VM."
  value       = azurerm_subnet.publica.id
}

output "subred_privada_id" {
  description = "Subred donde ira PostgreSQL."
  value       = azurerm_subnet.privada.id
}

output "nsg_publica_nombre" {
  description = "NSG que usaremos en el experimento de drift."
  value       = azurerm_network_security_group.publica.name
}
