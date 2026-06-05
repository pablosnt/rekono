"""Context-local storage utilities for the Rekono framework.

Provides request context propagation across the full request lifecycle,
making the active HTTP request available to any component without requiring
explicit parameter passing.
"""

from typing import Any

from asgiref.local import Local


class RequestContext:
    """Context-local storage for the active HTTP request.

    Stores the active HTTP request in a context-local variable so any component
    (models, serializers, background logic) can access request metadata such as
    the authenticated user and source IP without receiving the request as a
    parameter.

    Uses asgiref.local.Local to isolate state per thread (WSGI) or per async
    task (ASGI), ensuring concurrent requests never share or overwrite each
    other's context.

    Attributes:
        _local (Local): Context-local storage container, isolated per thread or async task.
    """

    _local = Local()

    @classmethod
    def set(cls, request: Any) -> None:
        """Store the active request for the current thread or async task.

        Args:
            request (Any): Incoming HTTP request to store as current context.
        """
        cls._local.request = request

    @classmethod
    def get(cls) -> Any:
        """Retrieve the active request for the current thread or async task.

        Returns:
            Any: The active HTTP request, or None if called outside a request lifecycle.
        """
        return getattr(cls._local, "request", None)

    @classmethod
    def clear(cls) -> None:
        """Remove the active request from context-local storage.

        Must be called in a finally block after request processing to ensure the
        context is always reset before the thread or async task is reused.
        """
        cls._local.request = None
