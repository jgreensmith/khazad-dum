variable "servers" {
  description = "AWS experiment servers to create, keyed by <experiment>__<name>."
  type = map(object({
    name          = string
    region        = string
    experiment    = string
    instance_type = string
    role          = string # "remote" (server side) for AWS endpoints
    bundle_dir    = string # local dir staged by khazad-dum (listener + payload + bootstrap.sh)
    listener_port = number # control port the khazad-dum listener binds
  }))
  default = {}
}

variable "keys_dir" {
  description = "Directory holding per-experiment SSH keypairs (<keys_dir>/<experiment>/id_rsa)."
  type        = string
}
