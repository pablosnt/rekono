"""ZAP executor for isolated home directory management.

Gives every ZAP execution its own temporary home directory so concurrent
scans don't collide on ZAP's shared default home.
"""

import shutil
import socket
import tempfile
from pathlib import Path

from tools.executors.base import BaseExecutor


class Zap(BaseExecutor):
    """Executor for OWASP ZAP that isolates concurrent scans.

    ZAP defaults to a single shared home directory (~/.ZAP), so two executions
    running at the same time collide with a "home directory already in use"
    error. This executor gives each execution its own temporary home directory
    via ZAP's -dir flag and removes it once the scan finishes.

    ZAP also starts its main proxy on port 8080 by default, even in command
    (-cmd) mode, so a run fails with "Address already in use" whenever another
    service holds 8080 or another scan runs at the same time. This executor
    binds the proxy to a free port picked at runtime to avoid both collisions.

    Attributes:
        zap_home (Path | None): Temporary ZAP home directory for this execution.
    """

    zap_home: Path | None = None

    def before_running(self) -> None:
        """Allocate an isolated home directory and proxy port for this run.

        Creates a fresh temporary directory and appends it to the arguments
        through ZAP's -dir flag so this execution never shares state with any
        concurrent scan. Also binds ZAP's main proxy to a free port, obtained by
        letting the operating system assign an ephemeral one, so it never
        collides with port 8080 (its default) or with another running scan.
        """
        self.zap_home = Path(tempfile.mkdtemp(prefix="zap-"))
        self.arguments.extend(["-dir", str(self.zap_home)])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            self.arguments.extend(["-config", f"network.localServers.mainProxy.port={sock.getsockname()[1]}"])

    def after_running(self) -> None:
        """Remove the temporary home directory created for this execution."""
        if self.zap_home and self.zap_home.is_dir():
            shutil.rmtree(self.zap_home, ignore_errors=True)
