import logging
from typing import Any


class LoggingFilter(logging.Filter):
    """Custom logging filter that adds request context to log records.

    This filter enhances log records with source IP address and user information
    extracted from Django request objects. It handles both authenticated and
    anonymous requests.
    """

    def filter(self, record: Any) -> bool:
        """Filter and enhance log records with request context.

        Adds source_ip and user fields to the log record based on request
        information. Handles both records with and without request data.

        Args:
            record: The log record to process.

        Returns:
            Always returns True to allow all records through.
        """
        if hasattr(record, "request"):
            # Record with request data
            record.source_ip = record.request.META.get("REMOTE_ADDR")
            record.user = "anonymous"  # Anonymous user by default
            if hasattr(record.request, "user") and record.request.user and record.request.user.id:
                # Authenticated request
                record.user = record.request.user.id
        else:
            # Record without request data
            record.source_ip = record.source_ip if hasattr(record, "source_ip") else ""
            record.user = record.user if hasattr(record, "user") else "anonymous"
        return True


class LoggingEntity:
    """Mixin class that provides logging capabilities to other classes.

    This class provides a shared logger instance that can be used by
    any class that inherits from it.

    Attributes:
        logger: Shared logging.Logger instance for the application.
    """

    logger = logging.getLogger()
