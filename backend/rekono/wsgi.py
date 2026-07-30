"""WSGI entry point for the Rekono Django project.

Exposes the WSGI callable as the module-level ``application`` variable, used
by WSGI-compatible servers to serve the platform.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rekono.settings")

application = get_wsgi_application()
