from rest_framework.routers import SimpleRouter

from parameters.views import InputTechnologyViewSet, InputVulnerabilityViewSet

router = SimpleRouter()
router.register('parameters/technologies', InputTechnologyViewSet)
router.register('parameters/technologies', InputVulnerabilityViewSet)

urlpatterns = router.urls
