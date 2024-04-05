from alerts.views import AlertViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("alerts", AlertViewSet)

urlpatterns = router.urls
