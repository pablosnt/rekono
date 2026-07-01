"""URL configuration for alerts module.

Defines URL patterns for the alerts REST API endpoints, including
alert management routes.
"""

from rest_framework.routers import SimpleRouter

from alerts.views import AlertViewSet

router = SimpleRouter()
router.register("alerts", AlertViewSet)

urlpatterns = router.urls
