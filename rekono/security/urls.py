from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from security.views import LogoutView, RekonoTokenObtainPairView

# Register your views here.

router = SimpleRouter()
router.register('logout', LogoutView, basename='logout')

urlpatterns = [
    path('token/', RekonoTokenObtainPairView.as_view(), name='token-pair'),     # Get access and refresh tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),   # Refresh access token
    path('', include(router.urls))
]
