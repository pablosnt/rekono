"""URL configuration for parameters REST API endpoints.

Defines URL patterns for input parameter management API using Django REST framework
router to register ViewSet endpoints for technology and vulnerability parameters.
"""

from rest_framework.routers import SimpleRouter

from parameters.views import InputTechnologyViewSet, InputVulnerabilityViewSet

router = SimpleRouter()
router.register("parameters/technologies", InputTechnologyViewSet)
router.register("parameters/vulnerabilities", InputVulnerabilityViewSet)

urlpatterns = router.urls
