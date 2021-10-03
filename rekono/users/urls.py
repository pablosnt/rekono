from django.urls import path
from rest_framework.routers import SimpleRouter
from users.views import (ChangeUserPasswordView, ChangeUserRoleView,
                         CreateUserView, DisableUserView, InviteUserView,
                         UserViewSet)

router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('users/invite', InviteUserView.as_view()),
    path('users/<int:pk>', CreateUserView.as_view()),
    path('users/<int:pk>/role', ChangeUserRoleView.as_view()),
    path('users/<int:pk>/change-password', ChangeUserPasswordView.as_view()),
    path('users/<int:pk>/disable', DisableUserView.as_view())
]
urlpatterns.extend(router.urls)
