from rest_framework.routers import SimpleRouter

from parameters.views import InputTechnologyViewSet, InputVulnerabilityViewSet

router = SimpleRouter()
router.register('parameters/technologies', InputTechnologyViewSet)
router.register('parameters/vulnerabilities', InputVulnerabilityViewSet)

urlpatterns = router.urls
