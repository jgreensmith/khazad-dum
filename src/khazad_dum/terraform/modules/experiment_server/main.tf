terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

# Latest Canonical Ubuntu 22.04 LTS (amd64, hvm-ssd) in this region.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "ssh" {
  name        = "khazad-dum-experiments"
  description = "khazad-dum experiment SSH + listener/app access"
  vpc_id      = data.aws_vpc.default.id

  # SSH from anywhere: khazad-dum delivers the provisioning bundle over SSH to
  # the public IP at provision time.
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Listener control plane + experiment app traffic arrive via the in-VPC
  # Twingate connector (private IPs), so allow all TCP/UDP/ICMP from the VPC —
  # not the public internet.
  ingress {
    description = "Listener + experiment traffic (in-VPC, via Twingate connector)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  experiments = toset([for s in var.servers : s.experiment])
}

resource "aws_key_pair" "this" {
  for_each   = local.experiments
  key_name   = "khazad-dum-${each.value}"
  public_key = file("${var.keys_dir}/${each.value}/id_rsa.pub")
}

resource "aws_instance" "this" {
  for_each = var.servers

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = each.value.instance_type
  key_name               = aws_key_pair.this[each.value.experiment].key_name
  vpc_security_group_ids = [aws_security_group.ssh.id]

  tags = {
    Name       = each.value.name
    Experiment = each.value.experiment
    ManagedBy  = "khazad-dum"
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("${var.keys_dir}/${each.value.experiment}/id_rsa")
    host        = self.public_ip
  }

  # Deliver the whole bundle directory (listener + payload + generated
  # bootstrap.sh) and run the bootstrap. The bootstrap (generated per endpoint
  # by khazad-dum) installs the listener as a systemd service and runs the
  # project payload's provisioning. Role/port/payload paths are baked into it.
  provisioner "file" {
    source      = "${each.value.bundle_dir}/"
    destination = "/tmp/khazad-bundle"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/khazad-bundle/bootstrap.sh",
      "sudo bash /tmp/khazad-bundle/bootstrap.sh",
    ]
  }
}
