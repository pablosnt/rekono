from findings.views import (CredentialViewSet, PathViewSet,
                            PortViewSet, ExploitViewSet, HostViewSet,
                            OSINTViewSet, TechnologyViewSet,
                            VulnerabilityViewSet)
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register('osint', OSINTViewSet)
router.register('hosts', HostViewSet)
router.register('ports', PortViewSet)
router.register('paths', PathViewSet)
router.register('technologies', TechnologyViewSet)
router.register('vulnerabilities', VulnerabilityViewSet)
router.register('credentials', CredentialViewSet)
router.register('exploits', ExploitViewSet)

urlpatterns = router.urls
