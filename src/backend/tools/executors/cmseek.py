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

    Handles CMSeek execution for CMS fingerprinting and security analysis.
    Manages result file relocation from CMSeek's default output directory
    to the configured report location.
    
    Attributes:
        Inherits all attributes from BaseExecutor
    """
    def after_running(self) -> None:
        """Handle post-execution cleanup and result file management.
        
        Moves CMSeek result files from the default output directory to the
        configured report location and cleans up temporary directories.
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
