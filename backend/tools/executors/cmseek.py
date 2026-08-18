"""Executor of the CMSeek CMS scanner."""

import shutil
import uuid
from pathlib import Path
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Cmseek(BaseExecutor):
    """Execution of CMSeek, which decides itself where to write its report.

    CMSeek builds the path of its report from the host and the port that it
    scanned, so the path has to be rebuilt from the scanned URL to find it.
    """

    def before_running(self) -> None:  # pragma: no cover
        """Give CMSeek a writable directory to run in.

        CMSeek writes its reports inside its own installation directory, and only
        falls back to the working directory when that one isn't writable, which is
        what happens when CMSeek is installed from a system package owned by root.
        """
        self.execution_directory = CONFIG.reports / str(uuid.uuid4())
        self.execution_directory.mkdir(parents=True, exist_ok=True)

    def after_running(self) -> None:  # pragma: no cover
        """Move the report that CMSeek wrote to the path where Rekono expects it."""
        result_path = (
            Path("Result")
            / urlparse(self.arguments[self.arguments.index("-u") + 1]).netloc.replace(":", "_")
            / "cms.json"
        )
        for report in [
            (self.execution_directory or Path()) / result_path,
            Path(CONFIG.cmseek_dir) / result_path,
        ]:
            if report.is_file():
                shutil.move(report, self.report)
                shutil.rmtree(report.parent)
                # CMSeek also writes an index of its reports in the working directory, which
                # would grow with every execution
                result_index = report.parent.parent.parent / "reports.json"
                if result_index.is_file():
                    result_index.unlink()
                break
        # The report was already moved to the path where Rekono keeps it
        if self.execution_directory and self.execution_directory.is_dir():
            shutil.rmtree(self.execution_directory, ignore_errors=True)
