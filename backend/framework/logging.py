"""Logging infrastructure shared by the whole Rekono backend.

The log format includes the source IP address and the user of each record, so the
filter defined here resolves both values from the active request, and the mixin
gives any class the logger that those records must be written to.
"""

import logging
from typing import Any

from framework.context import RequestContext


class LoggingFilter(logging.Filter):
    """Filter that adds the source IP address and the user to the log records."""

    def filter(self, record: Any) -> bool:
        """Add the source_ip and user attributes to the log record.

        Resolves the active request from the log record's extra data first,
        falling back to RequestContext for log records emitted by components
        that do not receive the request directly (models, serializers, etc.).

        When no request is available, source_ip and user are left untouched
        if the record already carries them, since background jobs and bot
        handlers pass a user id via the logger's extra instead of a request.
        Otherwise they default to an empty source_ip and an "anonymous" user.

        Args:
            record: Log record to enrich, modified in place.

        Returns:
            Always True, since the filter enriches the records instead of
            discarding them.
        """
        request = getattr(record, "request", None) or RequestContext.get()
        if request:
            record.source_ip = request.META.get("REMOTE_ADDR")
            record.user = "anonymous"
            if hasattr(request, "user") and request.user and request.user.id:
                record.user = request.user.id
        else:
            record.source_ip = record.source_ip if hasattr(record, "source_ip") else ""
            record.user = record.user if hasattr(record, "user") else "anonymous"
        return True


class LoggingEntity:
    """Mixin that provides the Rekono logger to the classes that write logs.

    The logger is the root logger rather than a per-class or per-module one, since
    Rekono's logging configuration only attaches the LoggingFilter and handlers to
    the "root" logger; %(module)s in the log format is what identifies the origin of
    each record.

    Attributes:
        logger: Root logger, shared by every class using this mixin.
    """

    logger = logging.getLogger()
