from django.urls import path, include
from rest_framework.routers import SimpleRouter
from users.views import (ChangeUserPasswordView, ChangeUserRoleView,
                         CreateUserView, DisableUserView, InviteUserView,
                         ResetUserPasswordView, UserViewSet)

router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('users/invite', InviteUserView.as_view()),
    path('users/change-password', ChangeUserPasswordView.as_view()),
    path('users/reset-password', ResetUserPasswordView.as_view()),
    path('users/<int:pk>', CreateUserView.as_view()),
    path('users/<int:pk>/role', ChangeUserRoleView.as_view()),
    path('users/<int:pk>/disable', DisableUserView.as_view()),
    path('', include(router.urls))
]
