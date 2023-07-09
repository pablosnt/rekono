from resources.views import WordlistViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register('wordlists', WordlistViewSet)

urlpatterns = router.urls
