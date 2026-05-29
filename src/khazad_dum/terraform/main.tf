provider "aws" {
  region = "eu-west-2"
}

provider "twingate" {
  api_token = var.tg_api_token
  network   = var.tg_network
}

provider "docker" {
  host = "ssh://james@computron.local"
}

locals {
  # Project each endpoint down to the fields the AWS module needs (avoids
  # passing homelab-only attributes like docker_image into the module type).
  aws_servers = {
    for k, s in var.servers : k => {
      name          = s.name
      experiment    = s.experiment
      region        = s.region
      instance_type = s.instance_type
      role          = s.role
      bundle_dir    = s.bundle_dir
      listener_port = s.listener_port
    } if s.target == "aws"
  }

  homelab_servers = { for k, s in var.servers : k => s if s.target == "homelab" }

  # Twingate connectors are EC2 instances — only create them for AWS experiments.
  aws_experiments = toset([for s in local.aws_servers : s.experiment])
}

# ── AWS experiment servers (the "remote app") ─────────────────────────────────

module "experiment_server" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = local.aws_servers
}

# ── Homelab (computron.local) experiment containers (the "local app") ─────────

resource "docker_image" "homelab" {
  for_each     = local.homelab_servers
  name         = each.value.docker_image
  keep_locally = true
}

resource "docker_container" "homelab" {
  for_each = local.homelab_servers
  image    = docker_image.homelab[each.key].image_id
  name     = replace(each.key, "__", "-")
  restart  = "unless-stopped"
  must_run = true

  # The listener is the container's long-lived process. It waits for the
  # provisioning step (below) to drop the listener + payload + config, then
  # execs it. Config (role/port/payload dir) is read from the JSON file.
  env = ["KHAZAD_LISTENER_CONFIG=/opt/khazad-dum/listener.config.json"]
  command = [
    "sh", "-c",
    "while [ ! -f /opt/khazad-dum/server.py ] || [ ! -f /opt/khazad-dum/listener.config.json ]; do sleep 1; done; exec python3 /opt/khazad-dum/server.py",
  ]

  labels {
    label = "experiment"
    value = each.value.experiment
  }

  labels {
    label = "managed-by"
    value = "khazad-dum"
  }
}

# Deliver the bundle (listener + payload + bootstrap.sh) into the container and
# run the bootstrap. The homelab bootstrap variant lays down the files + config
# the container command is waiting for, then runs the payload's provisioning.
resource "null_resource" "provision_homelab" {
  for_each = local.homelab_servers

  triggers = {
    bundle_dir   = each.value.bundle_dir
    container_id = docker_container.homelab[each.key].id
  }

  connection {
    type = "ssh"
    host = "computron.local"
    user = "james"
  }

  provisioner "file" {
    source      = "${each.value.bundle_dir}/"
    destination = "/tmp/khazad-bundle-${replace(each.key, "__", "-")}"
  }

  provisioner "remote-exec" {
    inline = [
      "docker exec ${replace(each.key, "__", "-")} mkdir -p /tmp/khazad-bundle",
      "docker cp /tmp/khazad-bundle-${replace(each.key, "__", "-")}/. ${replace(each.key, "__", "-")}:/tmp/khazad-bundle",
      "docker exec ${replace(each.key, "__", "-")} bash /tmp/khazad-bundle/bootstrap.sh",
    ]
  }

  depends_on = [docker_container.homelab]
}

# ── Twingate ──────────────────────────────────────────────────────────────────

# AWS side: a remote network + connector (EC2) per experiment.
data "aws_ami" "twingate_connector" {
  most_recent = true
  owners      = ["617935088040"]

  filter {
    name   = "name"
    values = ["twingate/images/hvm-ssd/twingate-amd64-*"]
  }
}

resource "twingate_remote_network" "experiment" {
  for_each = local.aws_experiments
  name     = "khazad-dum-${each.key}"
}

resource "twingate_connector" "experiment" {
  for_each          = local.aws_experiments
  remote_network_id = twingate_remote_network.experiment[each.key].id
}

resource "twingate_connector_tokens" "experiment" {
  for_each     = local.aws_experiments
  connector_id = twingate_connector.experiment[each.key].id
}

resource "aws_security_group" "twingate_connector" {
  name        = "khazad-dum-twingate-connector"
  description = "Twingate connector outbound-only"

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "twingate_connector" {
  for_each                    = local.aws_experiments
  ami                         = data.aws_ami.twingate_connector.id
  instance_type               = "t3.micro"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.twingate_connector.id]

  user_data = <<-EOT
    #!/bin/bash
    mkdir -p /etc/twingate/
    {
      echo TWINGATE_URL="https://${var.tg_network}.twingate.com"
      echo TWINGATE_ACCESS_TOKEN="${twingate_connector_tokens.experiment[each.key].access_token}"
      echo TWINGATE_REFRESH_TOKEN="${twingate_connector_tokens.experiment[each.key].refresh_token}"
    } > /etc/twingate/connector.conf
    systemctl enable --now twingate-connector
  EOT

  tags = {
    Name       = "khazad-dum-connector-${each.key}"
    Experiment = each.key
    ManagedBy  = "khazad-dum"
  }
}

# Expose each AWS endpoint (private IP) over its experiment's tunnel.
resource "twingate_resource" "server" {
  for_each          = module.experiment_server.servers
  name              = each.value.name
  address           = each.value.private_ip
  remote_network_id = twingate_remote_network.experiment[each.value.experiment].id

  protocols = {
    allow_icmp = true
    tcp = {
      policy = "ALLOW_ALL"
    }
    udp = {
      policy = "ALLOW_ALL"
    }
  }
}

# Homelab side: the connector already runs on computron, so we only add a
# resource for the experiment container inside the EXISTING remote network it
# serves. The address is the container's IP on computron's Docker network.
data "twingate_remote_network" "homelab" {
  name = var.tg_homelab_remote_network
}

resource "twingate_resource" "homelab" {
  for_each          = docker_container.homelab
  name              = local.homelab_servers[each.key].name
  address           = each.value.network_data[0].ip_address
  remote_network_id = data.twingate_remote_network.homelab.id

  protocols = {
    allow_icmp = true
    tcp = {
      policy = "ALLOW_ALL"
    }
    udp = {
      policy = "ALLOW_ALL"
    }
  }
}
