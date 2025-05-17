from platforms.cvecrowd.views import CveCrowdSettingsViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("cvecrowd", CveCrowdSettingsViewSet)

urlpatterns = router.urls
