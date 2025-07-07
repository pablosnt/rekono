from rest_framework.routers import SimpleRouter

from platforms.cvecrowd.views import CveCrowdSettingsViewSet

# Register your views here.

router = SimpleRouter()
router.register("cvecrowd", CveCrowdSettingsViewSet)

urlpatterns = router.urls
