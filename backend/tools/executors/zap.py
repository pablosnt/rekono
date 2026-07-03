"""ZAP executor for isolated home directory management.

Gives every ZAP execution its own temporary home directory so concurrent
scans don't collide on ZAP's shared default home.
"""

import shutil
import tempfile
from pathlib import Path

from tools.executors.base import BaseExecutor


class Zap(BaseExecutor):
    """Executor for OWASP ZAP that isolates concurrent scans.

    ZAP defaults to a single shared home directory (~/.ZAP), so two executions
    running at the same time collide with a "home directory already in use"
    error. This executor gives each execution its own temporary home directory
    via ZAP's -dir flag and removes it once the scan finishes.

    Attributes:
        zap_home (Path | None): Temporary ZAP home directory for this execution.
    """

    zap_home: Path | None = None

    def before_running(self) -> None:
        """Allocate an isolated home directory for this run.

        Creates a fresh temporary directory and appends it to the arguments
        through ZAP's -dir flag so this execution never shares state with any
        concurrent scan.
        """
        self.zap_home = Path(tempfile.mkdtemp(prefix="zap-"))
        self.arguments.extend(["-dir", str(self.zap_home)])

    def after_running(self) -> None:
        """Remove the temporary home directory created for this execution."""
        if self.zap_home and self.zap_home.is_dir():
            shutil.rmtree(self.zap_home, ignore_errors=True)
