"""CMSeek executor for CMS detection and security scanning.

Executes CMSeek tool for Content Management System detection, version
fingerprinting, and vulnerability assessment with result file management.
"""

import pathlib
import shutil
from pathlib import Path
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Cmseek(BaseExecutor):
    """Executor for CMSeek CMS detection tool.

    CMSeek writes its JSON result to a path it derives internally from the
    scanned host and port, rather than to the report path Rekono expects.
    This executor reconstructs that path from the scanned URL, then locates
    and moves the resulting file to ``self.report`` once the scan finishes.
    """

    def after_running(self) -> None:  # pragma: no cover
        """Handle post-execution cleanup and result file management.

        Moves CMSeek result files from the default output directory to the
        configured report location and cleans up temporary directories. Also
        removes the ``reports.json`` index CMSeek writes into the current working
        directory, which would otherwise accumulate across executions.
        """
        result_path = (
            Path("Result")
            / urlparse(self.arguments[self.arguments.index("-u") + 1]).netloc.replace(":", "_")
            / "cms.json"
        )
        for report in [result_path, Path(CONFIG.cmseek_dir) / result_path]:
            if report.is_file():
                shutil.move(report, self.report)
                shutil.rmtree(pathlib.Path(report).parent)
                result_index = Path("reports.json")
                if result_index.is_file():
                    result_index.unlink()
