"""GitLeaks executor for Git repository secret detection.

Executes GitLeaks tool with Git repository dumping capabilities to extract
secrets from exposed Git repositories and source code analysis.
"""

import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Gitleaks(BaseExecutor):
    """Executor for GitLeaks secret detection tool.

    Handles Git repository dumping and secret scanning by first attempting to
    dump exposed Git repositories using GitDumper, then running GitLeaks on
    the extracted source code to find sensitive information.

    Attributes:
        git_directory_dumped (bool): Whether Git repository was successfully dumped
        execution_directory (Path | None): Directory where Git repository was dumped
    """

    git_directory_dumped = False
    execution_directory = None

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:
        """Execute GitLeaks with Git repository dumping.

        First attempts to dump the Git repository using GitDumper, then runs
        GitLeaks on the extracted content if successful. Handles both scenarios
        where Git repository is available and where it's not.

        Args:
            environment (dict[str, Any]): Environment variables for execution
        """
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
