from rest_framework.routers import SimpleRouter

from authentications.views import AuthenticationViewSet

router = SimpleRouter()
router.register('authentications', AuthenticationViewSet)

urlpatterns = router.urls
