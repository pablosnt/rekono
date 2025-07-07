from rest_framework.routers import SimpleRouter

from reporting.views import ReportingViewSet

# Register your views here.

router = SimpleRouter()
router.register("reports", ReportingViewSet)

urlpatterns = router.urls
