from integrations.defect_dojo.views import (
    DefectDojoEngagementViewSet,
    DefectDojoProductTypeViewSet,
    DefectDojoProductViewSet,
    DefectDojoSettingsViewSet,
    DefectDojoSyncViewSet,
)
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("defect-dojo/settings", DefectDojoSettingsViewSet)
router.register("defect-dojo/sync", DefectDojoSyncViewSet)
router.register(
    "defect-dojo/product-type",
    DefectDojoProductTypeViewSet,
    basename="defect-dojo_product-type",
)
router.register(
    "defect-dojo/product", DefectDojoProductViewSet, basename="defect-dojo_product"
)
router.register(
    "defect-dojo/engagement",
    DefectDojoEngagementViewSet,
    basename="defect-dojo_engagement",
)

urlpatterns = router.urls
