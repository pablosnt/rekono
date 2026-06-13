"""Django REST framework views for Content Security Policy violation reporting.

Provides two unauthenticated endpoints that receive CSP violation reports from
browsers and emit them as structured warning log entries for security monitoring.
Handles the ``report-to`` Reporting API format and the legacy ``report-uri``
format through separate concrete view classes that share a common parsing base.
"""

import json
import logging
import unicodedata
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger()


class CspReportView(APIView):
    """Base view for receiving and logging Content Security Policy violation reports.

    Provides the shared parsing and dispatch logic for CSP violation ingestion.
    Parses the raw JSON request body and delegates each violation record to
    ``_process_violation``, which concrete subclasses override to extract fields
    from the format they handle. Always returns HTTP 204 so browsers do not treat
    a non-2xx response as a reason to suppress future reports.

    Attributes:
        authentication_classes (list): Empty — browsers send reports without credentials.
        permission_classes (list): Empty — no authentication required for violation delivery.
    """

    authentication_classes = []
    permission_classes = []

    def _sanitize(self, value: str | None) -> str | None:
        """Remove control characters and cap the length of a report field.

        Args:
            value (str | None): Raw, attacker-controlled field from the violation report.

        Returns:
            str | None: The value with control characters removed and length capped.
        """
        if not value:
            return value
        # Cap the length of each value, then drop every character whose unicode category starts
        # with "C" (control, format, surrogate, etc.) so CR/LF and other separators can't forge logs
        return "".join(char for char in value[:1000] if not unicodedata.category(char).startswith("C"))

    def _log_violation(self, blocked: str | None, origin: str | None, directive: str | None) -> None:
        """Emit a structured warning log entry for a single CSP violation.

        Args:
            blocked (str | None): URI of the resource that was blocked by the policy.
            origin (str | None): URI of the document where the violation occurred, or
                ``None`` if the report did not include it.
            directive (str | None): CSP directive that triggered the block
                (e.g. ``script-src``), or ``None`` if absent from the report.
        """
        if blocked and directive:
            logger.warning(
                f"[Content-Security-Policy] URI {self._sanitize(blocked)} has been blocked{f' in {self._sanitize(origin)}' if origin else ''} due to {self._sanitize(directive)} directive"
            )

    def _process_violation(self, data: dict[str, Any]) -> None:
        """Extract violation fields from a single report object and log them.

        Subclasses override this method to handle their specific report schema.
        The base implementation is a no-op so that ``CspReportView`` itself is
        never registered as a route.

        Args:
            data (dict[str, Any]): A single violation object parsed from the request body.
        """

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        """Ingest a CSP violation report and return HTTP 204.

        Parses the raw request body as JSON. The Reporting API delivers an array
        of report objects while ``report-uri`` delivers a single object, so both
        shapes are normalised to a list before dispatching to ``_process_violation``.
        Malformed payloads are silently discarded to avoid surfacing internal errors
        to the browser.

        Args:
            request (Request): HTTP request carrying the CSP report payload.
            *args (object): Additional positional arguments.
            **kwargs (object): Additional keyword arguments.

        Returns:
            Response: HTTP 204 No Content unconditionally.
        """
        try:
            body = json.loads(request.body)
        except Exception:  # pragma: no cover
            # Discard unparseable payloads — browsers occasionally send empty or malformed bodies
            return Response(status=status.HTTP_204_NO_CONTENT)
        for violation in body if isinstance(body, list) else [body]:
            self._process_violation(violation)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(exclude=True)
class CspReportToView(CspReportView):
    """CSP violation endpoint for the Reporting API (``report-to`` directive).

    Handles JSON payloads delivered by browsers that support the W3C Reporting
    API. Each element in the array is a report object whose ``type`` field identifies
    its category; only ``csp-violation`` entries are processed and logged.
    """

    def _process_violation(self, data: dict[str, Any]) -> None:
        """Extract and log a violation from a Reporting API report object.

        Filters out non-CSP report types before extracting fields, since the
        Reporting API multiplexes different report categories over the same
        endpoint (e.g. ``deprecation``, ``intervention``, ``csp-violation``).

        Args:
            data (dict[str, Any]): A single Reporting API report object.
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
    """CSP violation endpoint for the legacy ``report-uri`` directive.

    Handles JSON payloads delivered by browsers using the older ``report-uri``
    CSP directive. The payload is always a single JSON object (not an array)
    containing a ``csp-report`` key with the violation details.
    """

    def _process_violation(self, data: dict[str, Any]) -> None:
        """Extract and log a violation from a ``report-uri`` payload object.

        Args:
            data (dict[str, Any]): The top-level ``application/csp-report`` payload object.
        """
        report = data.get("csp-report", {})
        self._log_violation(
            report.get("blocked-uri"),
            report.get("document-uri"),
            report.get("effective-directive") or report.get("violated-directive"),
        )
