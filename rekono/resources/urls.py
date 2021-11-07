from resources.views import WordlistViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('reources/wordlists', WordlistViewSet)

urlpatterns = router.urls
