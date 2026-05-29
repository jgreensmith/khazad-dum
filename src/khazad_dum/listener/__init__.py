"""khazad-dum experiment listener.

The listener is *fixed infrastructure*: the same stdlib-only HTTP service is
installed on every experiment endpoint (the AWS "remote app" host and the
homelab "local app" container) at provision time. It exposes a stable control
contract that ``khazad-dum`` calls over the Twingate tunnel:

    GET  /health   -> liveness + role
    POST /run      -> start the project payload's experiment (non-blocking)
    GET  /status   -> idle | running | done | failed
    GET  /results  -> tar.gz of the payload's results/ directory

What the listener *runs* is project-specific: a **payload** authored by the
Experiment-phase gate workflow (an executable ``run`` plus a ``results/`` dir).
The listener never knows what protocol is being benchmarked — it just runs the
payload and serves whatever lands in ``results/``. See ``server.py`` for the
contract details.
"""

from .server import Config, load_config, serve

__all__ = ["Config", "load_config", "serve"]
