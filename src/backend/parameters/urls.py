from parameters.views import InputTechnologyViewSet, InputVulnerabilityViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("parameters/technologies", InputTechnologyViewSet)
router.register("parameters/vulnerabilities", InputVulnerabilityViewSet)

urlpatterns = router.urls
