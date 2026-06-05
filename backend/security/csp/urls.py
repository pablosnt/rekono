"""URL configuration for Content Security Policy reporting endpoints.

Defines two distinct URL patterns for CSP violation ingestion: one for the modern
Reporting API (``report-to`` directive) and one for the legacy ``report-uri``
directive. Both paths are intentionally unauthenticated so browsers can deliver
reports without user credentials regardless of the current session state.
"""

from django.urls import path

from security.csp.views import CspReportToView, CspReportUriView

urlpatterns = [
    path("csp-report-to/", CspReportToView.as_view(), name="csp-report-to"),
    path("csp-report-uri/", CspReportUriView.as_view(), name="csp-report-uri"),
]
