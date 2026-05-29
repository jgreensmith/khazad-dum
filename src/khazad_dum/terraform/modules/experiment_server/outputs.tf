output "servers" {
  description = "Provisioned AWS endpoints, keyed by <experiment>__<name>."
  value = {
    for k, inst in aws_instance.this : k => {
      name          = var.servers[k].name
      experiment    = var.servers[k].experiment
      region        = var.servers[k].region
      role          = var.servers[k].role
      target        = "aws"
      listener_port = var.servers[k].listener_port
      # `address` is what reaches this endpoint over Twingate (the private IP,
      # exposed as a twingate_resource). public_ip/dns are kept for SSH/summary.
      address    = inst.private_ip
      private_ip = inst.private_ip
      public_ip  = inst.public_ip
      public_dns = inst.public_dns
    }
  }
}
