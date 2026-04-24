"""URL routing configuration for statistics and analytics API endpoints.

Defines URL patterns and router configuration for statistics ViewSets providing
comprehensive analytics data through REST API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from stats.views import (
    CredentialEvolutionViewSet,
    ExploitEvolutionViewSet,
    HostEvolutionViewSet,
    HostStatsViewSet,
    HostVulnerabilitiesStatsViewSet,
    OSINTEvolutionViewSet,
    PathEvolutionViewSet,
    PortEvolutionViewSet,
    PortStatsViewSet,
    RQStatsView,
    TechnologyEvolutionViewSet,
    TechnologyStatsViewSet,
    TriagingStatsViewSet,
    VulnerabilityCVEStatsViewSet,
    VulnerabilityCWEStatsViewSet,
    VulnerabilityEvolutionViewSet,
    VulnerabilityExploitCoverageStatsViewSet,
    VulnerabilityStatusStatsViewSet,
)

router = SimpleRouter()
router.register("stats/host-os", HostStatsViewSet, basename="host-os")
router.register("stats/host-vulnerabilities", HostVulnerabilitiesStatsViewSet, basename="host-vulnerabilities")
router.register("stats/port", PortStatsViewSet, basename="port")
router.register("stats/technology", TechnologyStatsViewSet, basename="technology")
router.register("stats/vulnerability-cve", VulnerabilityCVEStatsViewSet, basename="vulnerability-cve")
router.register("stats/vulnerability-cwe", VulnerabilityCWEStatsViewSet, basename="vulnerability-cwe")
router.register("stats/vulnerability-status", VulnerabilityStatusStatsViewSet, basename="vulnerability-status")
router.register("stats/triaging", TriagingStatsViewSet, basename="triaging")
router.register("stats/exploit-coverage", VulnerabilityExploitCoverageStatsViewSet, basename="exploit-coverage")
router.register("stats/osint-evolution", OSINTEvolutionViewSet, basename="osint-evolution")
router.register("stats/host-evolution", HostEvolutionViewSet, basename="host-evolution")
router.register("stats/port-evolution", PortEvolutionViewSet, basename="port-evolution")
router.register("stats/path-evolution", PathEvolutionViewSet, basename="path-evolution")
router.register("stats/technology-evolution", TechnologyEvolutionViewSet, basename="technology-evolution")
router.register("stats/credential-evolution", CredentialEvolutionViewSet, basename="credential-evolution")
router.register("stats/vulnerability-evolution", VulnerabilityEvolutionViewSet, basename="vulnerability-evolution")
router.register("stats/exploit-evolution", ExploitEvolutionViewSet, basename="exploit-evolution")

urlpatterns = [path("stats/rq/", RQStatsView.as_view(), name="rq-stats"), path("", include(router.urls))]
