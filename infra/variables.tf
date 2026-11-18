variable "region" {
  description = "Region de Azure donde se crean los recursos esta es la permitida en Azure for Students y dentro de la UE."
  type        = string
  default     = "denmarkeast"
}

variable "proyecto" {
  description = "Prefijo para nombrar los recursos."
  type        = string
  default     = "clouddata"
}

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