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
router.register("defect-dojo/settings", DefectDojoSettingsViewSet)
router.register("defect-dojo/sync", DefectDojoSyncViewSet)
router.register("defect-dojo/product-types", DefectDojoProductTypeViewSet, basename="defect-dojo_product-type")
router.register("defect-dojo/products", DefectDojoProductViewSet, basename="defect-dojo_product")
router.register("defect-dojo/engagements", DefectDojoEngagementViewSet, basename="defect-dojo_engagement")

urlpatterns = router.urls
