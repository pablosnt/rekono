"""URL routing configuration for the Rekono platform.

This module defines the main URL routing configuration for the Rekono security
testing platform, including API endpoints, admin interface, and documentation
routes with OpenAPI schema generation and interactive API documentation.

The schema, Swagger UI, and Redoc endpoints are explicitly configured with
AllowAny permissions so they remain publicly accessible regardless of the
project-wide DEFAULT_PERMISSION_CLASSES, which require authentication.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("alerts.urls")),
    path("api/", include("api_tokens.urls")),
    path("api/", include("authentications.urls")),
    path("api/", include("executions.urls")),
    path("api/", include("findings.urls")),
    path("api/", include("http_headers.urls")),
    path("api/", include("integrations.urls")),
    path("api/", include("notes.urls")),
    path("api/", include("parameters.urls")),
    path("api/", include("platforms.cvecrowd.urls")),
    path("api/", include("platforms.defectdojo.urls")),
    path("api/", include("platforms.mail.urls")),
    path("api/", include("platforms.nvdnist.urls")),
    path("api/", include("platforms.telegram_app.urls")),
    path("api/", include("platforms.virustotal.urls")),
    path("api/", include("platforms.vulncheck.urls")),
    path("api/", include("processes.urls")),
    path("api/", include("projects.urls")),
    path("api/", include("reporting.urls")),
    path("api/", include("security.authentication.urls")),
    path("api/", include("security.csp.urls")),
    path("api/", include("settings.urls")),
    path("api/", include("stats.urls")),
    path("api/", include("target_denylist.urls")),
    path("api/", include("target_ports.urls")),
    path("api/", include("targets.urls")),
    path("api/", include("tasks.urls")),
    path("api/", include("tools.urls")),
    path("api/", include("users.urls")),
    path("api/", include("wordlists.urls")),
    # OpenAPI specification
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny], authentication_classes=[]),
        name="schema",
    ),
    # Swagger-UI
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny], authentication_classes=[]),
        name="swagger-ui",
    ),
    # Redoc
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema", permission_classes=[AllowAny], authentication_classes=[]),
        name="redoc",
    ),
    path("", lambda request: redirect("swagger-ui")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
