"""URL routing configuration for reporting REST API endpoints.

Defines URL patterns and routing for security report management endpoints
using Django REST framework routers.
"""

from rest_framework.routers import SimpleRouter

from reporting.views import ReportingViewSet

router = SimpleRouter()
router.register("reports", ReportingViewSet)

urlpatterns = router.urls
