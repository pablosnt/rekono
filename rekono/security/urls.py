from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from security.views import LogoutView, RekonoTokenObtainPairView

router = SimpleRouter()
router.register('logout', LogoutView, basename='logout')

urlpatterns = [
    path('token/', RekonoTokenObtainPairView.as_view(), name='token-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('', include(router.urls))
]
