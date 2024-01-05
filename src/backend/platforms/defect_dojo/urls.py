from rest_framework.routers import SimpleRouter

from platforms.defect_dojo.views import (
    DefectDojoEngagementViewSet,
    DefectDojoProductTypeViewSet,
    DefectDojoProductViewSet,
    DefectDojoSettingsViewSet,
    DefectDojoSyncViewSet,
)

# Register your views here.

router = SimpleRouter()
router.register("defect-dojo/settings", DefectDojoSettingsViewSet)
router.register("defect-dojo/sync", DefectDojoSyncViewSet)
router.register(
    "defect-dojo/product-types",
    DefectDojoProductTypeViewSet,
    basename="defect-dojo_product-type",
)
router.register(
    "defect-dojo/products", DefectDojoProductViewSet, basename="defect-dojo_product"
)
router.register(
    "defect-dojo/engagements",
    DefectDojoEngagementViewSet,
    basename="defect-dojo_engagement",
)

urlpatterns = router.urls
