#Red virtual es la VPC EN AZURE ES vNet
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-${var.nombre_base}"
  location            = var.region
  resource_group_name = var.grupo_recursos
  address_space       = [var.espacio_direcciones]
  tags                = var.etiquetas
}

#Subred publica computo VM con docket
resource "azurerm_subnet" "publica" {
  name                 = "snet-publica"
  resource_group_name  = var.grupo_recursos
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subred_publica]
}

#Subred privada base de datos
resource "azurerm_subnet" "privada" {
  name                 = "snet-privada"
  resource_group_name  = var.grupo_recursos
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subred_privada]

  delegation {
    name = "postgresql"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

#Grupo de seguridad de la subred publica
#Solo la IP del administrador puede entrar, y solo a SSH y a la API.
#Todo lo demas desde internet lo bloquea la regla por defecto DenyAllInBound.
resource "azurerm_network_security_group" "publica" {
  name                = "nsg-${var.nombre_base}-publica"
  location            = var.region
  resource_group_name = var.grupo_recursos
  tags                = var.etiquetas

  security_rule {
    name                       = "permitir-ssh-admin"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.ip_permitida
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "permitir-api-admin"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["8000", "8001"]
    source_address_prefix      = var.ip_permitida
    destination_address_prefix = "*"
  }
}

#Grupo de seguridad de la subred privada
#PostgreSQL solo acepta conexiones desde la subred public.
resource "azurerm_network_security_group" "privada" {
  name                = "nsg-${var.nombre_base}-privada"
  location            = var.region
  resource_group_name = var.grupo_recursos
  tags                = var.etiquetas

  security_rule {
    name                       = "permitir-postgres-desde-publica"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = var.subred_publica
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "permitir-trafico-interno-subred"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.subred_privada
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "denegar-resto-de-la-vnet"
    priority                   = 4000
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "publica" {
  subnet_id                 = azurerm_subnet.publica.id
  network_security_group_id = azurerm_network_security_group.publica.id
}

resource "azurerm_subnet_network_security_group_association" "privada" {
  subnet_id                 = azurerm_subnet.privada.id
  network_security_group_id = azurerm_network_security_group.privada.id
}

#Tabla de rutas de la subred publica
resource "azurerm_route_table" "publica" {
  name                = "rt-${var.nombre_base}-publica"
  location            = var.region
  resource_group_name = var.grupo_recursos
  tags                = var.etiquetas

  route {
    name           = "salida-a-internet"
    address_prefix = "0.0.0.0/0"
    next_hop_type  = "Internet"
  }
}

resource "azurerm_subnet_route_table_association" "publica" {
  subnet_id      = azurerm_subnet.publica.id
  route_table_id = azurerm_route_table.publica.id
}

