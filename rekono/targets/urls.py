from rest_framework.routers import SimpleRouter

from targets.views import (TargetCredentialViewSet, TargetPortViewSet,
                           TargetTechnologyViewSet, TargetViewSet,
                           TargetVulnerabilityViewSet)

# Register your views here.

router = SimpleRouter()
router.register('targets', TargetViewSet)
router.register('target-ports', TargetPortViewSet)
router.register('target-technologies', TargetTechnologyViewSet)
router.register('target-vulnerabilities', TargetVulnerabilityViewSet)
router.register('target-credentials', TargetCredentialViewSet)

urlpatterns = router.urls
