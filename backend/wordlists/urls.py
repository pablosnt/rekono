"""URL configuration for wordlist API endpoints.

Defines URL routing for wordlist-related REST API endpoints using
Django REST framework's SimpleRouter.
"""

from rest_framework.routers import SimpleRouter

from wordlists.views import WordlistViewSet

router = SimpleRouter()
router.register("wordlists", WordlistViewSet)

urlpatterns = router.urls
