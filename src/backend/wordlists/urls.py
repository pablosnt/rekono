from rest_framework.routers import SimpleRouter

from wordlists.views import WordlistViewSet

router = SimpleRouter()
router.register("wordlists", WordlistViewSet)

urlpatterns = router.urls
