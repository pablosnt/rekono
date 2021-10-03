from users.views import InviteUserView, CreateUserView, ChangeUserRoleView, DisableUserView, UserViewSet
from django.urls import path
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('users/invite', InviteUserView.as_view()),
    path('users/<int:pk>', CreateUserView.as_view()),
    path('users/<int:pk>/role', ChangeUserRoleView.as_view()),
    path('users/<int:pk>/disable', DisableUserView.as_view())
]
urlpatterns.extend(router.urls)
