"""URL routing configuration for DefectDojo integration REST API endpoints.

Defines URL patterns and routing for DefectDojo integration management endpoints
using Django REST framework's SimpleRouter for standardized API structure.
Includes routes for settings, synchronization, and entity creation operations.
"""

from rest_framework.routers import SimpleRouter

from platforms.defectdojo.views import (
    DefectDojoEngagementViewSet,
    DefectDojoProductTypeViewSet,
    DefectDojoProductViewSet,
    DefectDojoSettingsViewSet,
    DefectDojoSyncViewSet,
)

router = SimpleRouter()
router.register("defectdojo/settings", DefectDojoSettingsViewSet)
router.register("defectdojo/sync", DefectDojoSyncViewSet)
router.register("defectdojo/product-types", DefectDojoProductTypeViewSet, basename="defectdojo_product-type")
router.register("defectdojo/products", DefectDojoProductViewSet, basename="defectdojo_product")
router.register("defectdojo/engagements", DefectDojoEngagementViewSet, basename="defectdojo_engagement")

urlpatterns = router.urls
