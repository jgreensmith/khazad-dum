# AWS endpoints only — kept for the build-time SSH summary (needs public_ip/dns).
output "servers" {
  description = "Provisioned AWS endpoints keyed by <experiment>__<name>."
  value       = module.experiment_server.servers
}

# All endpoints (AWS + homelab) the control plane needs to reach over Twingate.
# Each has at least {name, experiment, target, role, address, listener_port}.
output "endpoints" {
  description = "All experiment endpoints keyed by <experiment>__<name>."
  value = merge(
    module.experiment_server.servers,
    {
      for k, c in docker_container.homelab : k => {
        name          = local.homelab_servers[k].name
        experiment    = local.homelab_servers[k].experiment
        target        = "homelab"
        role          = local.homelab_servers[k].role
        address       = c.network_data[0].ip_address
        listener_port = local.homelab_servers[k].listener_port
      }
    },
  )
}
