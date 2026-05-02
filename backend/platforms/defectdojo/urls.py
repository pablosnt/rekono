"""URL routing configuration for DefectDojo integration REST API endpoints.

Defines URL patterns and routing for DefectDojo integration management endpoints
using Django REST framework's SimpleRouter for standardized API structure.
Includes routes for settings and synchronization management.
"""

from rest_framework.routers import SimpleRouter

from platforms.defectdojo.views import DefectDojoSettingsViewSet, DefectDojoSyncViewSet

router = SimpleRouter()
router.register("defectdojo/settings", DefectDojoSettingsViewSet)
router.register("defectdojo/sync", DefectDojoSyncViewSet)

urlpatterns = router.urls
