"""Access to the active HTTP request from anywhere in the code.

The request is stored in a context-local variable by the security middleware, so
models, serializers, and any other component can read the authenticated user or the
source IP address without receiving the request as a parameter.
"""

from typing import Any

from asgiref.local import Local


class RequestContext:
    """Context-local storage for the active HTTP request.

    Uses asgiref.local.Local to isolate the request per thread (WSGI) or per async
    task (ASGI), ensuring concurrent requests never share or overwrite each other's
    context.
    """

    _local = Local()

    @classmethod
    def set(cls, request: Any) -> None:
        """Store the active request for the current thread or async task.

        Args:
            request: Request being processed, which stays readable until clear is
              called.
        """
        cls._local.request = request

    @classmethod
    def get(cls) -> Any:
        """Get the active request being processed.

        Returns:
            The active request, or None outside the request lifecycle, such as in
            background jobs and management commands.
        """
        return getattr(cls._local, "request", None)

    @classmethod
    def clear(cls) -> None:
        """Remove the active request from the context-local storage.

        Must be called in a finally block after request processing to ensure the
        context is always reset before the thread or async task is reused.
        """
        cls._local.request = None
