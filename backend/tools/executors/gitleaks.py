"""GitLeaks executor for Git repository secret detection.

Executes GitLeaks tool with Git repository dumping capabilities to extract
secrets from exposed Git repositories by scanning their commit history.
"""

import os
import subprocess
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Gitleaks(BaseExecutor):
    """Executor for GitLeaks secret detection tool.

    Handles Git repository dumping and secret scanning by first attempting to
    dump exposed Git repositories using GitDumper, then running GitLeaks over
    the dumped repository's commit history to find sensitive information.

    Attributes:
        git_directory_dumped (bool): Whether Git repository was successfully dumped
        execution_directory (Path | None): Directory where Git repository was dumped
    """

    git_directory_dumped = False
    execution_directory = None

    def get_environment(self) -> dict[str, Any]:
        """Prepare the execution environment allowing git to read the dumped repository.

        Extends the base environment with a wildcard safe.directory setting so that
        GitLeaks (which shells out to the system git to walk the commit history) can
        operate on the dumped repository even when it's owned by a different user than
        the worker process, as happens on Docker volume mounts. Without it, git aborts
        with "detected dubious ownership" and no secret is scanned.

        Returns:
            dict[str, Any]: Environment variables for tool execution
        """
        return {
            **super().get_environment(),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "safe.directory",
            "GIT_CONFIG_VALUE_0": "*",
        }

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:  # pragma: no cover
        """Execute GitLeaks with Git repository dumping.

        First attempts to dump the Git repository using GitDumper and considers it
        exposed only when actual git objects are downloaded. GitLeaks then scans the
        dumped repository's commit history, so no working tree checkout is needed.
        Handles both scenarios where the Git repository is available and where it's not.

        Args:
            environment (dict[str, Any]): Environment variables for execution
        """
        self.git_directory_dumped = False
        target_url = environment.get("GIT_DUMPER_TARGET_URL", "")
        if target_url[-1] != "/":
            target_url += "/"
        target_url += ".git/"
        try:
            self.port_from_arguments = urlparse(target_url).port
        except Exception:
            pass
        gitdumper_directory = Path(CONFIG.gittools_dir) / "Dumper"
        self.execution_directory = CONFIG.reports / str(uuid.uuid4())
        process = subprocess.run(
            ["bash", "gitdumper.sh", target_url, self.execution_directory],
            capture_output=True,
            env=environment,
            cwd=gitdumper_directory,
        )
        # GitDumper always creates a .git skeleton, so the repository is only exposed when it actually contains git objects
        objects_directory = self.execution_directory / ".git" / "objects"
        self.git_directory_dumped = objects_directory.is_dir() and any(
            path.is_file() for path in objects_directory.rglob("*") if path.parent.name != "info"
        )
        if self.git_directory_dumped:
            super().run_tool(environment)
        else:
            if process.returncode > 0 and process.stderr:
                self.execution.output_plain = process.stderr.decode()
                self.execution.error()
            else:
                self.execution.output_plain = "No git repository exposed"
                self.execution.completed(self.hash)
            self.execution.save(update_fields=["output_plain"])
