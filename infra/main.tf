locals {
  nombre_base = "${var.proyecto}-${var.entorno}"
}

#Grupo de recursos de la aplicacion.
resource "azurerm_resource_group" "principal" {
  name     = "rg-${local.nombre_base}"
  location = var.region
  tags     = var.etiquetas
}