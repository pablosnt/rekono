from users.views import CreateUserView
from django.urls import path

urlpatterns = [
    path('users', CreateUserView.as_view())
]
