provider "aws" {
  region = "eu-west-2"
}

provider "twingate" {
  api_key = var.tg_api_key
  network = var.tg_network
}

provider "docker" {
  host = "ssh://james@computron.local"
}

locals {
  aws_servers     = { for k, s in var.servers : k => s if s.target == "aws" }
  homelab_servers = { for k, s in var.servers : k => s if s.target == "homelab" }

  # Twingate connectors are EC2 instances — only create them for AWS experiments.
  aws_experiments = toset([for s in local.aws_servers : s.experiment])
}

# ── AWS experiment servers ────────────────────────────────────────────────────

module "experiment_server" {
  source   = "./modules/experiment_server"
  keys_dir = var.keys_dir
  servers  = local.aws_servers
}

# ── Homelab (computron.local) experiment containers ──────────────────────────

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

  labels {
    label = "experiment"
    value = each.value.experiment
  }

  labels {
    label = "managed-by"
    value = "khazad-dum"
  }
}

# Mirror the AWS provisioner pattern: copy + exec the provision script via SSH.
resource "null_resource" "provision_homelab" {
  for_each = local.homelab_servers

  triggers = {
    provision_file = each.value.provision_file
    container_id   = docker_container.homelab[each.key].id
  }

  connection {
    type = "ssh"
    host = "computron.local"
    user = "james"
  }

  provisioner "file" {
    source      = each.value.provision_file
    destination = "/tmp/khazad-provision-${replace(each.key, "__", "-")}"
  }

  provisioner "remote-exec" {
    inline = [
      "docker cp /tmp/khazad-provision-${replace(each.key, "__", "-")} ${replace(each.key, "__", "-")}:/tmp/khazad-provision",
      "docker exec ${replace(each.key, "__", "-")} chmod +x /tmp/khazad-provision",
      "docker exec ${replace(each.key, "__", "-")} /tmp/khazad-provision",
    ]
  }

  depends_on = [docker_container.homelab]
}

# ── Twingate (AWS experiments only) ──────────────────────────────────────────

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

resource "twingate_resource" "server" {
  for_each          = module.experiment_server.servers
  name              = each.value.name
  address           = each.value.private_ip
  remote_network_id = twingate_remote_network.experiment[each.value.experiment].id

  protocols {
    allow_icmp = true
    tcp {
      policy = "ALLOW_ALL"
    }
    udp {
      policy = "ALLOW_ALL"
    }
  }
}
