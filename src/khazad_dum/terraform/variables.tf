variable "servers" {
  description = "Map of experiment servers, keyed by <experiment>__<name>. Managed by the khazad-dum CLI."
  type = map(object({
    name           = string
    experiment     = string
    provision_file = string
    target         = string           # "aws" or "homelab"
    region         = optional(string, "")
    instance_type  = optional(string, "")
    docker_image   = optional(string, "")
  }))
  default = {}
}

variable "keys_dir" {
  description = "Directory holding per-experiment SSH keypairs (<keys_dir>/<experiment>/id_rsa)."
  type        = string
}

variable "tg_api_key" {
  description = "Twingate API key (Settings > API in the Admin Console)."
  type        = string
  sensitive   = true
}

variable "tg_network" {
  description = "Twingate tenant name (the subdomain of your .twingate.com URL)."
  type        = string
}
