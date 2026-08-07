"""Executor of the CMSeek CMS scanner."""

import pathlib
import shutil
from pathlib import Path
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Cmseek(BaseExecutor):
    """Execution of CMSeek, which decides itself where to write its report.

    CMSeek builds the path of its report from the host and the port that it
    scanned, so the path has to be rebuilt from the scanned URL to find it.
    """

    def after_running(self) -> None:  # pragma: no cover
        """Move the report that CMSeek wrote to the path where Rekono expects it."""
        result_path = (
            Path("Result")
            / urlparse(self.arguments[self.arguments.index("-u") + 1]).netloc.replace(":", "_")
            / "cms.json"
        )
        for report in [result_path, Path(CONFIG.cmseek_dir) / result_path]:
            if report.is_file():
                shutil.move(report, self.report)
                shutil.rmtree(pathlib.Path(report).parent)
                # CMSeek also writes an index of its reports in the working directory, which
                # would grow with every execution
                result_index = Path("reports.json")
                if result_index.is_file():
                    result_index.unlink()
