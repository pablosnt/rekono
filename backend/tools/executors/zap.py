"""Executor of the OWASP ZAP web scanner."""

import socket

from tools.executors.base import BaseExecutor


class Zap(BaseExecutor):
    """Execution of ZAP, which needs to be isolated from the other ZAP executions.

    ZAP uses one home directory and one proxy port for everything that it runs, so
    two executions at the same time fail because the home directory is already in
    use or because the port is already bound. The home directory is the one that
    the base executor already creates for this execution and removes afterwards,
    since ZAP is one more tool that writes what it needs while it runs.
    """

    def before_running(self) -> None:
        """Give this execution its own home directory and its own proxy port."""
        super().before_running()
        self.arguments.extend(["-dir", str(self.execution_directory)])
        # The operating system assigns the port, so it's free even if something else is
        # already listening on the 8080 that ZAP uses by default
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            self.arguments.extend(["-config", f"network.localServers.mainProxy.port={sock.getsockname()[1]}"])
