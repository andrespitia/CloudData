variable "nombre_base" {
  description = "Prefijo para los nombres."
  type        = string
}

variable "region" {
  description = "Region de Azure."
  type        = string
}

variable "grupo_recursos" {
  description = "Grupo de recursos donde se crea la red."
  type        = string
}

variable "etiquetas" {
  description = "Etiquetas comunes."
  type        = map(string)
}

variable "espacio_direcciones" {
  description = "Rango de direcciones de la VNet."
  type        = string
  default     = "10.10.0.0/16"
}

variable "subred_publica" {
  description = "Rango de la subred publica."
  type        = string
  default     = "10.10.1.0/24"
}

variable "subred_privada" {
  description = "Rango de la subred privada de la base de datos."
  type        = string
  default     = "10.10.2.0/24"
}

variable "ip_permitida" {
  description = "Unica IP publica autorizada para SSH y la API."
  type        = string

  validation {
    condition     = can(cidrhost(var.ip_permitida, 0))
    error_message = "ip_permitida debe tener formato CIDR."
  }
}
