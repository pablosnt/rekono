"""Nikto executor for report file relocation.

Nikto treats the -output value as a filename prefix and appends the format
extension to it. This executor moves the resulting report to the path Rekono
expects so it can be parsed and served.
"""

from pathlib import Path

from tools.executors.base import BaseExecutor


class Nikto(BaseExecutor):
    """Executor for the Nikto web vulnerability scanner.

    Nikto treats the -output value as a filename prefix and appends the format
    extension to it, so an -output of ``<report>.xml`` produces the report at
    ``<report>.xml.xml``. Without correction Rekono looks for the report at the
    expected path, finds nothing, leaves the output file unset, and the parser
    has nothing to read. This executor relocates the produced file back to
    ``self.report`` so the report is parsed, stored, and downloadable.

    Attributes:
        Inherits all attributes from BaseExecutor
    """

    def after_running(self) -> None:  # pragma: no cover
        """Relocate Nikto's report to the expected path and register it.

        Nikto appends the format extension to the -output value, so the report is
        written to ``<report>.<format>``. Move it back to ``self.report`` and store
        the reference so the output file is parsed and shown to users.
        """
        extension = self.execution.configuration.tool.output_format
        if not extension:
            return
        produced = Path(f"{self.report}.{extension}")
        if produced.is_file():
            produced.replace(self.report)
            self.execution.output_file = self.report
            self.execution.save(update_fields=["output_file"])
