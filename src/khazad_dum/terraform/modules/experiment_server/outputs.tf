output "servers" {
  description = "Provisioned servers in this region, keyed by <experiment>__<name>."
  value = {
    for k, inst in aws_instance.this : k => {
      name       = var.servers[k].name
      experiment = var.servers[k].experiment
      region     = var.servers[k].region
      public_ip  = inst.public_ip
      public_dns = inst.public_dns
    }
  }
}
