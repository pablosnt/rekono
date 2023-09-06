from django.urls import include, path
from rest_framework.routers import SimpleRouter
from users.views import (
    CreateUserViewSet,
    ProfileViewSet,
    ResetPasswordViewSet,
    UserViewSet,
)

# Register your views here.

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("users/create", CreateUserViewSet)

profile = ProfileViewSet.as_view({"get": "get", "put": "update"})
update_password = ProfileViewSet.as_view({"put": "update_password"})
# telegram_token = ProfileViewSet.as_view({"post": "telegram_token"})
reset_password = ResetPasswordViewSet.as_view({"post": "create", "put": "update"})

urlpatterns = [
    # path('api-token/', views.obtain_auth_token),
    path("profile/", profile),
    path("security/update-password/", update_password),
    path("security/reset-password/", reset_password),
    # path("profile/telegram-token/", telegram_token),
    path("", include(router.urls)),
]
