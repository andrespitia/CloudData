locals {
  nombre_base = "${var.proyecto}-${var.entorno}"
}

#Grupo de recursos de la aplicacion.
resource "azurerm_resource_group" "principal" {
  name     = "rg-${local.nombre_base}"
  location = var.region
  tags     = var.etiquetas
}

#AGRESO LA CAPA DE RED AL MODULO MAIN 
module "red" {
  source = "./modules/red"

  nombre_base    = local.nombre_base
  region         = var.region
  grupo_recursos = azurerm_resource_group.principal.name
  etiquetas      = var.etiquetas
  ip_permitida   = var.ip_permitida
}