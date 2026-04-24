"""URL routing configuration for findings REST API endpoints.

Defines REST API routes for all finding types using Django REST Framework
router with ViewSet registration for comprehensive findings management.
"""

from rest_framework.routers import SimpleRouter

from findings.views import (
    CredentialViewSet,
    ExploitViewSet,
    HostViewSet,
    LatestHostsViewSet,
    LatestVulnerabilitiesViewSet,
    OSINTViewSet,
    PathViewSet,
    PortViewSet,
    TechnologyViewSet,
    VulnerabilityViewSet,
)

router = SimpleRouter()
router.register("hosts/latest", LatestHostsViewSet, basename="latest-hosts")
router.register("vulnerabilities/latest", LatestVulnerabilitiesViewSet, basename="latest-vulnerabilities")
router.register("osint", OSINTViewSet)
router.register("hosts", HostViewSet)
router.register("ports", PortViewSet)
router.register("paths", PathViewSet)
router.register("technologies", TechnologyViewSet)
router.register("vulnerabilities", VulnerabilityViewSet)
router.register("credentials", CredentialViewSet)
router.register("exploits", ExploitViewSet)

urlpatterns = router.urls
