from authentications.views import AuthenticationViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("authentications", AuthenticationViewSet)

urlpatterns = router.urls
