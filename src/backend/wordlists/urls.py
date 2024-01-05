from rest_framework.routers import SimpleRouter

from wordlists.views import WordlistViewSet

# Register your views here.

router = SimpleRouter()
router.register("wordlists", WordlistViewSet)

urlpatterns = router.urls
