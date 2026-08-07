"""URLs of the finding endpoints, one per kind of finding."""

from django.urls import include, path
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
router.register("osint", OSINTViewSet)
router.register("hosts", HostViewSet)
router.register("ports", PortViewSet)
router.register("paths", PathViewSet)
router.register("technologies", TechnologyViewSet)
router.register("vulnerabilities", VulnerabilityViewSet)
router.register("credentials", CredentialViewSet)
router.register("exploits", ExploitViewSet)

urlpatterns = [
    path("hosts/latest/", LatestHostsViewSet.as_view({"get": "list"}), name="latest-hosts"),
    path(
        "vulnerabilities/latest/", LatestVulnerabilitiesViewSet.as_view({"get": "list"}), name="latest-vulnerabilities"
    ),
    path("", include(router.urls)),
]
