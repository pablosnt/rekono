"""Logging infrastructure and utilities for Rekono framework.

Provides enhanced logging capabilities with request tracking,
user identification, and audit trail functionality.
"""

import logging
from typing import Any

from framework.context import RequestContext


class LoggingFilter(logging.Filter):
    """Custom logging filter for enriching log records with request context.

    Adds user identification and source IP information to log records
    for comprehensive audit trails and security monitoring.
    """

    def filter(self, record: Any) -> bool:
        """Enrich log records with user and request context information.

        Resolves the active request from the log record's extra data first,
        falling back to RequestContext for log records emitted by components
        that do not receive the request directly (models, serializers, etc.).
        Adds source_ip and user attributes to log records for comprehensive
        audit trails and security monitoring.

        When no request is available, source_ip and user are left untouched
        if the record already carries them, since background jobs and bot
        handlers pass a user id via the logger's extra instead of a request.
        Otherwise they default to an empty source_ip and an "anonymous" user.

        Args:
            record (Any): The log record to enrich.

        Returns:
            bool: Always True to allow all records through.
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
    """Mixin class providing logging capabilities to other classes.

    Provides a standardized logger instance for classes that need
    logging functionality throughout the Rekono platform. The logger is
    the root logger rather than a per-class or per-module one, since
    Rekono's logging configuration only attaches the LoggingFilter and
    handlers to the "root" logger; %(module)s in the log format is what
    identifies the origin of each record.

    Attributes:
        logger (Logger): Shared root logger instance, common to every class using this mixin.

    Example:
        ```python
        class MyClass(LoggingEntity):
            def process(self):
                self.logger.info("Processing started")
        ```
    """

    logger = logging.getLogger()
