"""Stdlib-only HTTP listener that runs a project's experiment payload.

Design goals:
- **Zero pip dependencies.** It must start on a bare Ubuntu host or a minimal
  container without installing anything, so it uses only the standard library.
- **Project-agnostic.** It runs an opaque *payload* (an executable ``run`` that
  writes into ``results/``) and serves the results. It knows nothing about the
  protocol under test.
- **Single run at a time.** An experiment endpoint runs one benchmark per
  ``khazad-dum start`` invocation; concurrent runs are rejected with 409.

Configuration (env vars; a JSON file named by ``KHAZAD_LISTENER_CONFIG`` is read
first as a base, then env vars override it):
- ``KHAZAD_LISTENER_PORT``  listen port (default 8080).
- ``KHAZAD_PAYLOAD_DIR``    dir containing the executable ``run`` (default cwd).
- ``KHAZAD_ROLE``           this endpoint's role: ``local`` or ``remote``.
- ``KHAZAD_PEER_ADDR``      the peer endpoint's Twingate address (may be empty).

Each ``POST /run`` launches ``<payload>/run`` with cwd = payload dir and these
env vars exported to it:
- ``KHAZAD_ROLE``, ``KHAZAD_PEER_ADDR`` — so a client payload knows where its
  server peer lives, and which side it is.
- ``KHAZAD_RESULTS_DIR`` — absolute path the payload must write outputs into.
- ``KHAZAD_RUN_ID`` — the current run id.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DEFAULT_PORT = 8080


@dataclass
class Config:
    port: int = DEFAULT_PORT
    payload_dir: Path = Path.cwd()
    role: str = ""
    peer_addr: str = ""

    @property
    def run_executable(self) -> Path:
        return self.payload_dir / "run"

    @property
    def results_dir(self) -> Path:
        return self.payload_dir / "results"

    @property
    def status_file(self) -> Path:
        return self.payload_dir / "status.json"


def load_config() -> Config:
    """Build a Config from an optional JSON file (base) overlaid with env vars."""
    data: dict = {}
    cfg_path = os.environ.get("KHAZAD_LISTENER_CONFIG")
    if cfg_path and Path(cfg_path).is_file():
        data = json.loads(Path(cfg_path).read_text())

    def pick(env_key: str, json_key: str, default: str) -> str:
        return os.environ.get(env_key, data.get(json_key, default))

    return Config(
        port=int(pick("KHAZAD_LISTENER_PORT", "port", str(DEFAULT_PORT))),
        payload_dir=Path(pick("KHAZAD_PAYLOAD_DIR", "payload_dir", str(Path.cwd()))).resolve(),
        role=pick("KHAZAD_ROLE", "role", ""),
        peer_addr=pick("KHAZAD_PEER_ADDR", "peer_addr", ""),
    )


class ExperimentRunner:
    """Owns the single experiment subprocess and its observable state."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._proc: subprocess.Popen | None = None
        self._run_id: str | None = None
        self._state = "idle"  # idle | running | done | failed
        self._exit_code: int | None = None
        self._started: float | None = None
        self._ended: float | None = None

    # -- queries -------------------------------------------------------------
    def status(self) -> dict:
        with self._lock:
            self._refresh_locked()
            return {
                "role": self._config.role,
                "state": self._state,
                "run_id": self._run_id,
                "exit_code": self._exit_code,
                "started": self._started,
                "ended": self._ended,
            }

    def is_running(self) -> bool:
        with self._lock:
            self._refresh_locked()
            return self._state == "running"

    # -- actions -------------------------------------------------------------
    def start(self, peer_addr: str | None = None) -> dict:
        """Launch the payload's ``run`` non-blocking. Raises if already running.

        ``peer_addr`` overrides the configured peer for this run — khazad-dum
        learns each endpoint's Twingate address from terraform outputs only
        after apply, so it injects the peer at /run time.
        """
        with self._lock:
            self._refresh_locked()
            if self._state == "running":
                raise RuntimeError("an experiment is already running")

            run_exe = self._config.run_executable
            if not run_exe.is_file():
                raise FileNotFoundError(f"payload entrypoint not found: {run_exe}")

            # Fresh results dir per run so /results only reflects the latest run.
            results = self._config.results_dir
            if results.exists():
                shutil.rmtree(results)
            results.mkdir(parents=True, exist_ok=True)

            run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            env = os.environ.copy()
            env.update(
                KHAZAD_ROLE=self._config.role,
                KHAZAD_PEER_ADDR=peer_addr or self._config.peer_addr,
                KHAZAD_RESULTS_DIR=str(results),
                KHAZAD_RUN_ID=run_id,
            )
            log = open(results / "run.log", "wb")  # noqa: SIM115 (closed by watcher)
            self._proc = subprocess.Popen(
                [str(run_exe)],
                cwd=str(self._config.payload_dir),
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            self._run_id = run_id
            self._state = "running"
            self._exit_code = None
            self._started = time.time()
            self._ended = None
            self._write_status_locked()
            threading.Thread(target=self._watch, args=(self._proc, log), daemon=True).start()
            return {"run_id": run_id, "state": "running"}

    # -- internals -----------------------------------------------------------
    def _watch(self, proc: subprocess.Popen, log) -> None:
        proc.wait()
        log.close()
        with self._lock:
            if proc is self._proc:
                self._refresh_locked()

    def _refresh_locked(self) -> None:
        """Reconcile state with the live process (call with the lock held)."""
        if self._proc is None or self._state != "running":
            return
        code = self._proc.poll()
        if code is None:
            return
        self._exit_code = code
        self._state = "done" if code == 0 else "failed"
        self._ended = time.time()
        self._write_status_locked()

    def _write_status_locked(self) -> None:
        payload = {
            "role": self._config.role,
            "state": self._state,
            "run_id": self._run_id,
            "exit_code": self._exit_code,
            "started": self._started,
            "ended": self._ended,
        }
        try:
            self._config.status_file.write_text(json.dumps(payload, indent=2))
        except OSError:
            pass  # status file is best-effort; never crash the run on it


def _make_handler(config: Config, runner: ExperimentRunner):
    class Handler(BaseHTTPRequestHandler):
        server_version = "khazad-dum-listener/1.0"

        def _send_json(self, code: int, body: dict) -> None:
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args) -> None:  # quieter, but keep a line
            print(f"[listener] {self.address_string()} {fmt % args}", flush=True)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send_json(200, {"status": "ok", "role": config.role})
            elif self.path == "/status":
                self._send_json(200, runner.status())
            elif self.path == "/results":
                self._send_results()
            else:
                self._send_json(404, {"error": "not found", "path": self.path})

        def do_POST(self) -> None:
            if self.path == "/run":
                peer_addr = self._read_peer_addr()
                try:
                    self._send_json(202, runner.start(peer_addr=peer_addr))
                except RuntimeError as exc:
                    self._send_json(409, {"error": str(exc)})
                except FileNotFoundError as exc:
                    self._send_json(500, {"error": str(exc)})
            else:
                self._send_json(404, {"error": "not found", "path": self.path})

        def _read_peer_addr(self) -> str | None:
            """Optional ``{"peer_addr": "..."}`` body overriding the configured peer."""
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0:
                return None
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
                value = body.get("peer_addr")
                return str(value) if value else None
            except (ValueError, AttributeError):
                return None

        def _send_results(self) -> None:
            results = config.results_dir
            if runner.is_running():
                self._send_json(409, {"error": "experiment still running"})
                return
            if not results.is_dir() or not any(results.iterdir()):
                self._send_json(404, {"error": "no results yet"})
                return
            with tempfile.NamedTemporaryFile(suffix=".tar.gz") as tmp:
                with tarfile.open(fileobj=tmp, mode="w:gz") as tar:
                    tar.add(results, arcname="results")
                size = tmp.tell()
                tmp.seek(0)
                self.send_response(200)
                self.send_header("Content-Type", "application/gzip")
                self.send_header("Content-Length", str(size))
                self.send_header(
                    "Content-Disposition", 'attachment; filename="results.tar.gz"'
                )
                self.end_headers()
                shutil.copyfileobj(tmp, self.wfile)

    return Handler


def serve(config: Config | None = None) -> None:
    config = config or load_config()
    config.payload_dir.mkdir(parents=True, exist_ok=True)
    runner = ExperimentRunner(config)
    handler = _make_handler(config, runner)
    httpd = ThreadingHTTPServer(("0.0.0.0", config.port), handler)
    print(
        f"[listener] role={config.role or '?'} port={config.port} "
        f"payload={config.payload_dir} peer={config.peer_addr or '-'}",
        flush=True,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    # Allows the file to run standalone on an endpoint (``python3 server.py``)
    # without the khazad_dum package being importable there.
    serve()
