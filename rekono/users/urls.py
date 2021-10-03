from users.views import InviteUserView, CreateUserView, UserViewSet
from django.urls import path
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('users/invite', InviteUserView.as_view()),
    path('users/<int:pk>', CreateUserView.as_view())
]
urlpatterns.extend(router.urls)
