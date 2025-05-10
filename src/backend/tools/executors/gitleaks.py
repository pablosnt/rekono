import os
import subprocess  # nosec
import uuid
from pathlib import Path
from typing import Any

from executions.models import Execution
from findings.enums import Severity
from findings.models import Vulnerability
from rekono.settings import CONFIG
from tools.executors.base import BaseExecutor


class Gitleaks(BaseExecutor):
    def __init__(self, execution: Execution) -> None:
        super().__init__(execution)
        self.git_directory_dumped = False

    def _parse_findings(self, output: str) -> None:
        super()._parse_findings(output)
        if self.git_directory_dumped:
            self.parser.create_finding(
                Vulnerability,
                name="Git source code exposure",
                description=(
                    "Source code is exposed in the endpoint /.git/ and it's possible to dump it as a git repository"
                ),
                severity=Severity.HIGH,
                # CWE-527: Exposure of Version-Control Repository to an Unauthorized Control Sphere
                cwe="CWE-527",
                reference="https://iosentrix.com/blog/git-source-code-disclosure-vulnerability/",
            )

    def _run(self, environment: dict[str, Any] = os.environ.copy()) -> str:
        target_url = environment.get("GIT_DUMPER_TARGET_URL", "")
        if target_url[-1] != "/":
            target_url += "/"
        target_url += ".git/"
        gitdumper_directory = Path(CONFIG.gittools_dir) / "Dumper"
        run_directory = CONFIG.reports / str(uuid.uuid4())
        process = subprocess.run(  # nosec
            ["bash", gitdumper_directory, "gitdumper.sh", target_url, run_directory],
            capture_output=True,
            cwd=gitdumper_directory,
        )
        subprocess.run(  # nosec
            ["git", "checkout", "--", "."],
            capture_output=True,
            cwd=run_directory,
        )
        for path in self.run_directory.iterdir():
            if path.stem != ".git" or path.is_file():
                self.git_directory_dumped = True
                break
        if self.git_directory_dumped:
            return super()._run(environment)
        if process.returncode > 0:
            raise RuntimeError(process.stderr.decode("utf-8"))
        return process.stdout.decode("utf-8")
