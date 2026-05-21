output "servers" {
  description = "Provisioned servers keyed by <experiment>__<name>."
  value = merge(
    module.us_east_1.servers,
    module.us_east_2.servers,
    module.us_west_2.servers,
    module.eu_west_1.servers,
    module.eu_west_2.servers,
    module.eu_central_1.servers,
  )
}
