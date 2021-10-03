from users.views import InviteUserView, CreateUserView
from django.urls import path

urlpatterns = [
    path('users/invite', InviteUserView.as_view()),
    path('users/<int:pk>', CreateUserView.as_view())
]
