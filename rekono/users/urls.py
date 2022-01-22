from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter
from users.views import (CreateUserViewSet, ResetPasswordViewSet,
                         UserAdminViewSet, UserProfileViewSet)

# Register your views here.

router = SimpleRouter()
router.register('users', UserAdminViewSet)

profile = UserProfileViewSet.as_view({'get': 'get_profile', 'put': 'update_profile'})
change_password = UserProfileViewSet.as_view({'put': 'change_password'})
telegram_token = UserProfileViewSet.as_view({'post': 'telegram_token'})
reset_password = ResetPasswordViewSet.as_view({'post': 'create', 'put': 'reset_password'})

urlpatterns = [
    path('api-token/', views.obtain_auth_token),
    path('users/create/', CreateUserViewSet.as_view({'post': 'create'})),
    path('reset-password/', reset_password),
    path('profile/', profile),
    path('profile/change-password/', change_password),
    path('profile/telegram-token/', telegram_token),
    path('', include(router.urls)),
]
