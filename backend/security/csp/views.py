"""Endpoints that receive the CSP violation reports sent by the browsers.

There is one view per delivery format, the modern Reporting API and the legacy
``report-uri`` directive, and both log the violations they receive.
"""

import json
import unicodedata
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from framework.logging import LoggingEntity


class CspReportView(APIView, LoggingEntity):
    """Base view that parses the CSP violation reports and logs them.

    Attributes:
        authentication_classes: None, since the browsers deliver the reports
          without any credential.
        permission_classes: None, for the same reason.
    """

    authentication_classes = []
    permission_classes = []

    def _sanitize(self, value: str | None) -> str | None:
        """Clean a value of the report before it's written to the logs.

        Args:
            value: Untrusted value taken from the report, or None.

        Returns:
            The value capped at 1000 characters and without the characters that
            could forge log entries, or the value unchanged when it's empty, since
            there is nothing to sanitize then.
        """
        if not value:
            return value
        # Cap the length of each value, then drop every character whose unicode category starts
        # with "C" (control, format, surrogate, etc.) so CR/LF and other separators can't forge logs
        return "".join(char for char in value[:1000] if not unicodedata.category(char).startswith("C"))

    def _log_violation(self, blocked: str | None, origin: str | None, directive: str | None) -> None:
        """Log one CSP violation, if the report identifies what was blocked and why.

        Args:
            blocked: URI of the resource that was blocked by the policy.
            origin: URI of the document where the violation occurred, or None if the
              report didn't include it.
            directive: CSP directive that blocked the resource, like ``script-src``.
        """
        if blocked and directive:
            self.logger.warning(
                f"[Content-Security-Policy] URI {self._sanitize(blocked)} has been blocked{f' in {self._sanitize(origin)}' if origin else ''} due to {self._sanitize(directive)} directive"
            )

    def _process_violation(self, data: dict[str, Any]) -> None:
        """Read one violation from the report, as each delivery format does.

        Args:
            data: One report of the payload, whose shape depends on the format.
        """

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Receive a CSP report and log the violations that it contains.

        The Reporting API delivers an array of reports while ``report-uri`` delivers
        a single one, so both shapes are normalized to a list. Malformed payloads
        are discarded, and the response is always 204, so a browser never takes an
        error as a reason to stop reporting.

        Args:
            request: Request whose body holds the report, in the format of the view.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty 204 response, even when the payload can't be parsed.
        """
        try:
            body = json.loads(request.body)
        except Exception as ex:  # pragma: no cover
            self.logger.error(f"[{self.__class__.__name__}] Error parsing a CSP report: {str(ex)}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        for violation in body if isinstance(body, list) else [body]:
            self._process_violation(violation)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(exclude=True)
class CspReportToView(CspReportView):
    """Receive the reports of the browsers that support the Reporting API."""

    def _process_violation(self, data: dict[str, Any]) -> None:
        """Read one violation from a Reporting API report.

        The Reporting API multiplexes different report categories over the same
        endpoint (e.g. ``deprecation``, ``intervention``, ``csp-violation``), so the
        reports that aren't CSP violations are ignored.

        Args:
            data: One report of the array delivered by the Reporting API.
        """
        if data.get("type", "").lower() == "csp-violation":
            report = data.get("body", {})
            self._log_violation(
                report.get("blockedURL"),
                report.get("documentUrl") or data.get("url"),
                report.get("effectiveDirective"),
            )


@extend_schema(exclude=True)
class CspReportUriView(CspReportView):
    """Receive the reports that the ``report-uri`` directive asks the browsers for."""

    def _process_violation(self, data: dict[str, Any]) -> None:
        """Read the violation from a ``report-uri`` payload.

        Args:
            data: Payload delivered by the browser, wrapping the violation in its
              ``csp-report`` key.
        """
        report = data.get("csp-report", {})
        self._log_violation(
            report.get("blocked-uri"),
            report.get("document-uri"),
            report.get("effective-directive") or report.get("violated-directive"),
        )
