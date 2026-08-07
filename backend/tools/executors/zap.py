"""Executor of the OWASP ZAP web scanner."""

import shutil
import socket
import tempfile
from pathlib import Path

from tools.executors.base import BaseExecutor


class Zap(BaseExecutor):
    """Execution of ZAP, which needs to be isolated from the other ZAP executions.

    ZAP uses one home directory and one proxy port for everything that it runs, so
    two executions at the same time fail because the home directory is already in
    use or because the port is already bound.

    Attributes:
        zap_home: Temporary home directory that this execution uses.
    """

    zap_home: Path | None = None

    def before_running(self) -> None:
        """Give this execution its own home directory and its own proxy port."""
        self.zap_home = Path(tempfile.mkdtemp(prefix="zap-"))
        self.arguments.extend(["-dir", str(self.zap_home)])
        # The operating system assigns the port, so it's free even if something else is
        # already listening on the 8080 that ZAP uses by default
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            self.arguments.extend(["-config", f"network.localServers.mainProxy.port={sock.getsockname()[1]}"])

    def after_running(self) -> None:
        """Remove the home directory that this execution used."""
        if self.zap_home and self.zap_home.is_dir():
            shutil.rmtree(self.zap_home, ignore_errors=True)
