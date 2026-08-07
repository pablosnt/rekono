"""URLs of the report endpoints."""

from rest_framework.routers import SimpleRouter

from reporting.views import ReportingViewSet

router = SimpleRouter()
router.register("reports", ReportingViewSet)

urlpatterns = router.urls
