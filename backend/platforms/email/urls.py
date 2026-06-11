"""URL routing configuration for email platform REST API endpoints.

Defines URL patterns and routing for SMTP settings management endpoints
using Django REST framework's SimpleRouter for standardized API structure.
"""

from rest_framework.routers import SimpleRouter

from platforms.email.views import SMTPSettingsViewSet

router = SimpleRouter()
router.register("smtp", SMTPSettingsViewSet)

urlpatterns = router.urls
