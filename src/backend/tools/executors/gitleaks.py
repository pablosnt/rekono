import os
import subprocess
import uuid
from functools import cached_property
from pathlib import Path
from typing import Any

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Gitleaks(BaseExecutor):
    git_directory_dumped = False
    run_directory = None

    @cached_property
    def _execution_directory(self) -> Path | None:
        return self.run_directory

    def _run(self, environment: dict[str, Any] = os.environ.copy()) -> None:
        self.git_directory_dumped = False
        target_url = environment.get("GIT_DUMPER_TARGET_URL", "")
        if target_url[-1] != "/":
            target_url += "/"
        target_url += ".git/"
        # pytype: disable=attribute-error
        gitdumper_directory = Path(CONFIG.gittools_dir) / "Dumper"
        # pytype: enable=attribute-error
        self.run_directory = CONFIG.reports / str(uuid.uuid4())
        process = subprocess.run(
            ["bash", "gitdumper.sh", target_url, self.run_directory],
            capture_output=True,
            env=environment,
            cwd=gitdumper_directory,
        )
        if self.run_directory.is_dir():
            subprocess.run(["git", "checkout", "--", "."], env=environment, cwd=self.run_directory)
            for path in self.run_directory.iterdir():
                if path.stem != ".git" or path.is_file():
                    self.git_directory_dumped = True
                    break
        if self.git_directory_dumped:
            super()._run(environment)
        else:
            self.execution.output_plain = "No git repository exposed"
            if process.returncode > 0:
                if process.stderr:
                    self.execution.output_plain = process.stderr
                    self.execution.save(update_fields=["output_plain"])
                    self._on_error()
                    return
            self._on_completed()
