"""URL configuration for VirusTotal platform REST API endpoints.

This module defines the URL routing configuration for VirusTotal platform
management API endpoints, providing RESTful access to platform settings
and configuration management.
"""

from rest_framework.routers import SimpleRouter

from platforms.virustotal.views import VirusTotalSettingsViewSet

router = SimpleRouter()
router.register("virustotal", VirusTotalSettingsViewSet)

urlpatterns = router.urls
