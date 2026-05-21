variable "servers" {
  description = "Map of experiment servers, keyed by <experiment>__<name>. Managed by the khazad-dum CLI."
  type = map(object({
    name           = string
    region         = string
    experiment     = string
    provision_file = string
    instance_type  = string
  }))
  default = {}
}

variable "keys_dir" {
  description = "Directory holding per-experiment SSH keypairs (<keys_dir>/<experiment>/id_rsa)."
  type        = string
}
