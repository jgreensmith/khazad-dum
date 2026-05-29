"""Entry point: ``python -m khazad_dum.listener`` (or the standalone copy
dropped on an endpoint, run as ``python3 -m listener`` / ``python3 server.py``).

Provisioning installs this package on each endpoint and starts it under a
process supervisor (systemd on the AWS host, the container's foreground command
on the homelab container).
"""

from .server import serve

if __name__ == "__main__":
    serve()
