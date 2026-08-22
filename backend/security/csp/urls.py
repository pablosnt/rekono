"""URLs where the browsers deliver the CSP violation reports.

There is one endpoint for the modern Reporting API (``report-to`` directive) and
another one for the legacy ``report-uri`` directive. Both are unauthenticated, since
the browsers can't attach credentials when they deliver a report.
"""

from django.urls import path

from security.csp.views import CspReportToView, CspReportUriView

urlpatterns = [
    path("csp-report-to/", CspReportToView.as_view(), name="csp-report-to"),
    path("csp-report-uri/", CspReportUriView.as_view(), name="csp-report-uri"),
]
