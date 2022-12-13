from rest_framework.routers import SimpleRouter

from authentication.views import AuthenticationViewSet

router = SimpleRouter()
router.register('authentications', AuthenticationViewSet)

urlpatterns = router.urls
