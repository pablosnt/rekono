"""ASGI entry point for the Rekono Django project.

Exposes the ASGI callable as the module-level ``application`` variable, used
by ASGI-compatible servers to serve the platform.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rekono.settings")

application = get_asgi_application()
