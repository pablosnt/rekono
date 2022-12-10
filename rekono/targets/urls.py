from rest_framework.routers import SimpleRouter

from targets.views import (TargetAuthenticationViewSet, TargetPortViewSet,
                           TargetTechnologyViewSet, TargetViewSet,
                           TargetVulnerabilityViewSet)

# Register your views here.

router = SimpleRouter()
router.register('targets', TargetViewSet)
router.register('target-ports', TargetPortViewSet)
router.register('target-technologies', TargetTechnologyViewSet)
router.register('target-vulnerabilities', TargetVulnerabilityViewSet)
router.register('target-authentication', TargetAuthenticationViewSet)

urlpatterns = router.urls
