import logging
from typing import Any


class LoggingFilter(logging.Filter):
    def filter(self, record: Any) -> bool:
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
    logger = logging.getLogger()
