"""Executor of the Nikto web scanner."""

from pathlib import Path

from tools.executors.base import BaseExecutor


class Nikto(BaseExecutor):
    """Execution of Nikto, whose report ends up in an unexpected path.

    Nikto treats the value of its output argument as a prefix and appends the
    format extension to it, so the report is written next to the path that Rekono
    expects instead of in it, and nothing would be parsed.
    """

    def after_running(self) -> None:  # pragma: no cover
        """Move the report that Nikto wrote to the path where Rekono expects it."""
        extension = self.execution.configuration.tool.output_format
        if not extension:
            return
        produced = Path(f"{self.report}.{extension}")
        if produced.is_file():
            produced.replace(self.report)
            self.execution.output_file = self.report
            self.execution.save(update_fields=["output_file"])
