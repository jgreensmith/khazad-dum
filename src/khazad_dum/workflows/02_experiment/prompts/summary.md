# Experiment Infrastructure Summary

The data below describes the live experiment endpoints khazad-dum just provisioned for one WAN-comms
experiment: an AWS EC2 host (the **remote app**) and a Docker container on the home lab (the **local
app**), reachable over a Twingate TLS tunnel.

Produce a short operator briefing:
- One line per endpoint: name, target (aws/homelab), role (remote/local), Twingate address + listener
  port.
- For the AWS endpoint, include the exact SSH command shown (login user `ubuntu`, per-experiment key).
- End with the next steps in the pipeline: `khazad-dum start experiment` → `fetch experiment` →
  `graph experiment` → `report experiment`.

Be concise. Use only the data provided; do not invent hosts, IPs, or credentials.
