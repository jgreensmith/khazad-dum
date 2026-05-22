output "servers" {
  description = "Provisioned servers keyed by <experiment>__<name>."
  value       = module.experiment_server.servers
}
