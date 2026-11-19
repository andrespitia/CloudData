variable "region" {
  description = "Region de Azure donde se crean los recursos esta es la permitida en Azure for Students y dentro de la UE."
  type        = string
  default     = "denmarkeast"
}

#nombre del grupo de recursos
variable "proyecto" {
  description = "Prefijo para nombrar los recursos."
  type        = string
  default     = "clouddata"
}

#entorno de desarrollo nombre dev del grupo
variable "entorno" {
  description = "Entorno de despliegue."
  type        = string
  default     = "dev"
}

variable "etiquetas" {
  description = "Etiquetas comunes para todos los recursos."
  type        = map(string)
  default = {
    proyecto   = "CloudData"
    hito       = "3"
    gestionado = "terraform"
  }
}

variable "ip_permitida" {
  description = "IP publica del administrador en formato cidr en este caso mi ip."
  type        = string
}