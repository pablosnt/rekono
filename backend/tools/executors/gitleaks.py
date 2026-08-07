"""Executor of the GitLeaks secret scanner."""

import os
import subprocess
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Gitleaks(BaseExecutor):
    """Execution of GitLeaks, which needs a repository to scan.

    The repository is downloaded first with GitDumper, so the secrets are searched
    in the commit history of the Git repositories that a web server exposes.

    Attributes:
        git_directory_dumped: Whether the target exposed a repository to scan.
        execution_directory: Directory where the repository was downloaded.
    """

    git_directory_dumped = False
    execution_directory = None

    def get_environment(self) -> dict[str, Any]:
        """Get the environment variables that GitLeaks will be run with.

        Returns:
            The environment of the base executor, plus the configuration that lets
            git read a repository owned by another user, which is what happens with
            the Docker volumes, since git refuses to read it otherwise.
        """
        return {
            **super().get_environment(),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "safe.directory",
            "GIT_CONFIG_VALUE_0": "*",
        }

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:  # pragma: no cover
        """Download the repository of the target and search for secrets in it.

        The execution completes without findings if the target doesn't expose any
        repository, since that isn't an error.

        Args:
            environment: Environment variables to run the tools with.
        """
        self.git_directory_dumped = False
        target_url = environment.get("GIT_DUMPER_TARGET_URL", "")
        if target_url[-1] != "/":
            target_url += "/"
        target_url += ".git/"
        # The scanned port only appears in the URL of the environment, so it has to be taken
        # from there for the findings to be linked to it
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
        # GitDumper always creates a .git skeleton, so the repository is only exposed when it
        # actually contains git objects
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
