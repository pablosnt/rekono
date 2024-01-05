from reporting.views import ReportingViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("reports", ReportingViewSet)

urlpatterns = router.urls
