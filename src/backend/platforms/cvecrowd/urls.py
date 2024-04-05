from platforms.cvecrowd.views import CVECrowdSettingsViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("cvecrowd", CVECrowdSettingsViewSet)

urlpatterns = router.urls
