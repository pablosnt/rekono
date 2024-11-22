from django.urls import path
from stats.views import (
    ActivityStatsView,
    HostEvolutionView,
    HostStatsView,
    RQStatsView,
    TriagingStatsView,
    VulnerabilityEvolutionView,
    VulnerabilityStatsView,
)

urlpatterns = [
    path("stats/rq/", RQStatsView.as_view(), name="rq-stats"),
    path("stats/activity/", ActivityStatsView.as_view(), name="activity-stats"),
    path("stats/assets/", HostStatsView.as_view(), name="assets-stats"),
    path(
        "stats/assets/evolution/", HostEvolutionView.as_view(), name="assets-evolution"
    ),
    path(
        "stats/vulnerabilities/",
        VulnerabilityStatsView.as_view(),
        name="vulnerabilities-stats",
    ),
    path(
        "stats/vulnerabilities/evolution/",
        VulnerabilityEvolutionView.as_view(),
        name="vulnerabilities-evolution",
    ),
    path("stats/triaging/", TriagingStatsView.as_view(), name="triaging-stats"),
]
