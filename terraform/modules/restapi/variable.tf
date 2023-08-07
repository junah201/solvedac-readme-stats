variable "name" {
  type        = string
  description = "Name of the Rest API"
}

variable "description" {
  type        = string
  description = "Description of the Rest API"
  default     = ""
}

variable "lambdas" {
  type = list(
    string
  )
}

variable "domain_certificate_name" {
  type        = string
  description = "Domain certificate name"
}

variable "domain_name" {
  type        = string
  description = "Domain name"
}
