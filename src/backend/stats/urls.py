from django.urls import path
from stats.views import (
    ActivityStatsView,
    AssetsStatsView,
    RQStatsView,
    TriagingStatsView,
    VulnerabilityStatsView,
)

urlpatterns = [
    path("stats/rq/", RQStatsView.as_view(), name="rq-stats"),
    path("stats/activity/", ActivityStatsView.as_view(), name="activity-stats"),
    path("stats/assets/", AssetsStatsView.as_view(), name="assets-stats"),
    path(
        "stats/vulnerabilities/",
        VulnerabilityStatsView.as_view(),
        name="vulnerabilities-stats",
    ),
    path("stats/triaging/", TriagingStatsView.as_view(), name="triaging-stats"),
]
