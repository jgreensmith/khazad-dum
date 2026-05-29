variable "servers" {
  description = "Map of experiment endpoints, keyed by <experiment>__<name>. Managed by the khazad-dum CLI."
  type = map(object({
    name          = string
    experiment    = string
    target        = string                 # "aws" (remote app) or "homelab" (local app)
    role          = string                 # "remote" or "local"
    bundle_dir    = string                 # local dir khazad-dum staged: listener + payload + bootstrap.sh
    listener_port = optional(number, 8080) # control port the listener binds
    region        = optional(string, "")   # aws only
    instance_type = optional(string, "")   # aws only
    docker_image  = optional(string, "")   # homelab only (must provide python3 + bash, e.g. python:3.12-slim)
  }))
  default = {}
}

variable "keys_dir" {
  description = "Directory holding per-experiment SSH keypairs (<keys_dir>/<experiment>/id_rsa)."
  type        = string
}

variable "tg_api_token" {
  description = "Twingate API token (Settings > API in the Admin Console)."
  type        = string
  sensitive   = true
}

variable "tg_network" {
  description = "Twingate tenant name (the subdomain of your .twingate.com URL)."
  type        = string
}

variable "tg_homelab_remote_network" {
  description = "Name of the EXISTING Twingate remote network that your homelab connector (on computron) serves. The experiment container is exposed as a resource inside it."
  type        = string
}
