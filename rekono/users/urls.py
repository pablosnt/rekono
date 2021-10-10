from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter
from users.views import (ResetPasswordViewSet, UserAdminViewSet,
                         UserInitViewSet, UserProfileViewSet)

router = SimpleRouter()
router.register('users', UserAdminViewSet)
router.register('profile', UserProfileViewSet)

reset_password = ResetPasswordViewSet.as_view(
    {
        'post': 'create',
        'put': 'reset_password',
    }
)

urlpatterns = [
    path('api-token/', views.obtain_auth_token),
    path('users/<int:pk>/create/', UserInitViewSet.as_view({'post': 'create'})),
    path('reset-password/', reset_password),
    path('', include(router.urls)),
]
