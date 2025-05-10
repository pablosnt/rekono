import pathlib
import shutil
from pathlib import Path
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Cmseek(BaseExecutor):
    def _after_running(self) -> None:
        result_path = Path("Result") / urlparse(self.arguments(self.arguments.index("-u") + 1)).hostname / "cms.json"
        for report in [
            result_path,
            Path(CONFIG.cmseek_dir) / result_path,
        ]:
            if report.is_file():
                report.rename(self.report)
                shutil.rmtree(pathlib.Path(report).parent)
