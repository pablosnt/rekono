import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Gitleaks(BaseExecutor):
    git_directory_dumped = False
    execution_directory = None

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:
        self.git_directory_dumped = False
        target_url = environment.get("GIT_DUMPER_TARGET_URL", "")
        if target_url[-1] != "/":
            target_url += "/"
        target_url += ".git/"
        gitdumper_directory = Path(CONFIG.gittools_dir) / "Dumper"
        self.execution_directory = CONFIG.reports / str(uuid.uuid4())
        process = subprocess.run(
            ["bash", "gitdumper.sh", target_url, self.execution_directory],
            capture_output=True,
            env=environment,
            cwd=gitdumper_directory,
        )
        if self.execution_directory.is_dir():
            subprocess.run(["git", "checkout", "--", "."], env=environment, cwd=self.execution_directory)
            for path in self.execution_directory.iterdir():
                if path.stem != ".git" or path.is_file():
                    self.git_directory_dumped = True
                    break
        if self.git_directory_dumped:
            super().run_tool(environment)
        else:
            if process.returncode > 0 and process.stderr:
                self.execution.output_plain = process.stderr
                self.on_error()
            else:
                self.execution.output_plain = "No git repository exposed"
                self.on_completed()
            self.execution.save(update_fields=["output_plain"])
