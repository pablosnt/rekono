import os
import pathlib
import shutil
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Cmseek(BaseExecutor):
    def _after_running(self) -> None:
        result_path = os.path.join(
            "Result",
            urlparse(self.arguments(self.arguments.index("-u") + 1)).hostname,
            "cms.json",
        )
        for report in [
            result_path,
            os.path.join(CONFIG.cmseek_dir, result_path),
        ]:
            if os.path.isfile(report):
                shutil.move(report, self.report)
                shutil.rmtree(pathlib.Path(report).parent)
