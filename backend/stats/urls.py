"""URLs of the statistics endpoints.

The statistics are not resources, so they are routed one by one instead of being
registered in a router, and each URL only answers the list request.
"""

from django.urls import path

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

get_view = {"get": "list"}
urlpatterns = [
    path("stats/rq/", RQStatsView.as_view(), name="rq-stats"),
    path("stats/host-os/", HostStatsViewSet.as_view(get_view), name="host-os"),
    path("stats/host-vulnerabilities/", HostVulnerabilitiesStatsViewSet.as_view(get_view), name="host-vulnerabilities"),
    path("stats/port/", PortStatsViewSet.as_view(get_view), name="port"),
    path("stats/technology/", TechnologyStatsViewSet.as_view(get_view), name="technology"),
    path("stats/vulnerability-cve/", VulnerabilityCVEStatsViewSet.as_view(get_view), name="vulnerability-cve"),
    path("stats/vulnerability-cwe/", VulnerabilityCWEStatsViewSet.as_view(get_view), name="vulnerability-cwe"),
    path("stats/vulnerability-status/", VulnerabilityStatusStatsViewSet.as_view(get_view), name="vulnerability-status"),
    path("stats/triaging/", TriagingStatsViewSet.as_view(get_view), name="triaging"),
    path(
        "stats/exploit-coverage/", VulnerabilityExploitCoverageStatsViewSet.as_view(get_view), name="exploit-coverage"
    ),
    path("stats/osint-evolution/", OSINTEvolutionViewSet.as_view(get_view), name="osint-evolution"),
    path("stats/host-evolution/", HostEvolutionViewSet.as_view(get_view), name="host-evolution"),
    path("stats/port-evolution/", PortEvolutionViewSet.as_view(get_view), name="port-evolution"),
    path("stats/path-evolution/", PathEvolutionViewSet.as_view(get_view), name="path-evolution"),
    path("stats/technology-evolution/", TechnologyEvolutionViewSet.as_view(get_view), name="technology-evolution"),
    path("stats/credential-evolution/", CredentialEvolutionViewSet.as_view(get_view), name="credential-evolution"),
    path(
        "stats/vulnerability-evolution/",
        VulnerabilityEvolutionViewSet.as_view(get_view),
        name="vulnerability-evolution",
    ),
    path("stats/exploit-evolution/", ExploitEvolutionViewSet.as_view(get_view), name="exploit-evolution"),
]
