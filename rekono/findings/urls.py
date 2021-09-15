from findings.views import (EnumerationViewSet, ExploitViewSet, HostViewSet,
                            HttpEndpointViewSet, OSINTViewSet,
                            TechnologyViewSet, VulnerabilityViewSet)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('osint', OSINTViewSet)
router.register('hosts', HostViewSet)
router.register('enumeration', EnumerationViewSet),
router.register('endpoints', HttpEndpointViewSet),
router.register('technologies', TechnologyViewSet),
router.register('vulnerabilities', VulnerabilityViewSet),
router.register('exploits', ExploitViewSet)

urlpatterns = router.urls
