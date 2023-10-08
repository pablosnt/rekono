import json
import os
import subprocess
import uuid
from typing import Any, Dict, List

from executions.models import Execution
from findings.enums import Severity
from findings.models import Port, Vulnerability
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
                    "Source code is exposed in the endpoint /.git/ and "
                    "it's possible to dump it as a git repository"
                ),
                severity=Severity.HIGH,
                # CWE-527: Exposure of Version-Control Repository to an Unauthorized Control Sphere
                cwe="CWE-527",
                reference="https://iosentrix.com/blog/git-source-code-disclosure-vulnerability/",
            )

    def _run(self, environment: Dict[str, Any] = ...) -> str:
        target_url = environment.get("GIT_DUMPER_TARGET_URL", "")
        if target_url[-1] != "/":
            target_url += "/"
        target_url += ".git/"
        gitdumper_directory = os.path.join(CONFIG.gittools_dir, "Dumper")
        run_directory = os.path.join(CONFIG.reports, str(uuid.uuid4()))
        process = subprocess.run(
            ["bash", gitdumper_directory, "gitdumper.sh", target_url, run_directory],
            capture_output=True,
            cwd=gitdumper_directory,
        )
        subprocess.run(
            ["git", "checkout", "--", "."],
            capture_output=True,
            cwd=run_directory,
        )
        for _, dirs, files in os.walk(self.run_directory):
            # Check if Git repository has been dumped or not
            self.git_directory_dumped = (
                len([d for d in dirs if d != ".git"]) > 0 or len(files) > 0
            )
            break
        if self.git_directory_dumped:
            return super()._run(environment)
        if process.returncode > 0:
            raise RuntimeError(process.stderr.decode("utf-8"))
        return process.stdout.decode("utf-8")
