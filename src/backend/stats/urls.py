from django.urls import include, path
from rest_framework.routers import SimpleRouter

from stats.views import (
    HostEvolutionStatsViewSet,
    HostStatsViewSet,
    HostVulnerabilitiesStatsViewSet,
    LatestHostsViewSet,
    LatestTasksViewSet,
    LatestVulnerabilitiesViewSet,
    PortStatsViewSet,
    RQStatsView,
    TechnologyStatsViewSet,
    TopProjectsViewSet,
    TriagingStatsViewSet,
    VulnerabilityCVEStatsViewSet,
    VulnerabilityCWEStatsViewSet,
    VulnerabilityEvolutionStatsViewSet,
    VulnerabilityFixProgressPerServerityStatsViewSet,
    VulnerabilityFixProgressStatsViewSet,
    VulnerabilitySeverityStatsViewSet,
    VulnerabilityTrendingStatsViewSet,
)

router = SimpleRouter()
router.register("stats/latest-tasks", LatestTasksViewSet, basename="latest-tasks")
router.register("stats/latest-hosts", LatestHostsViewSet, basename="latest-hosts")
router.register("stats/latest-vulnerabilities", LatestVulnerabilitiesViewSet, basename="latest-vulnerabilities")
router.register("stats/top-projects", TopProjectsViewSet, basename="top-projects")
router.register("stats/host-os", HostStatsViewSet, basename="host-os")
router.register("stats/host-vulnerabilities", HostVulnerabilitiesStatsViewSet, basename="host-vulnerabilities")
router.register("stats/host-evolution", HostEvolutionStatsViewSet, basename="host-evolution")
router.register("stats/port", PortStatsViewSet, basename="host-os")
router.register("stats/technology", TechnologyStatsViewSet, basename="technologies")
router.register("stats/vulnerability-trending", VulnerabilityTrendingStatsViewSet, basename="vulnerability-trending")
router.register("stats/vulnerability-cve", VulnerabilityCVEStatsViewSet, basename="vulnerability-cve")
router.register("stats/vulnerability-cwe", VulnerabilityCWEStatsViewSet, basename="vulnerability-cwe")
router.register("stats/vulnerability-severity", VulnerabilitySeverityStatsViewSet, basename="vulnerability-severity")
router.register("stats/vulnerability-evolution", VulnerabilityEvolutionStatsViewSet, basename="vulnerability-evolution")
router.register("stats/vulnerability-fixes", VulnerabilityFixProgressStatsViewSet, basename="vulnerability-fixes")
router.register(
    "stats/vulnerability-fixes-per-severity",
    VulnerabilityFixProgressPerServerityStatsViewSet,
    basename="vulnerability-fixes-per-severity",
)
router.register("stats/triaging", TriagingStatsViewSet, basename="triaging")

urlpatterns = [path("stats/rq/", RQStatsView.as_view(), name="rq-stats"), path("", include(router.urls))]
