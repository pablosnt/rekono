from django.urls import path, include
from findings.views import (EnumerationEnableView, EnumerationViewSet,
                            ExploitEnableView, ExploitViewSet, HostEnableView,
                            HostViewSet, HttpEndpointEnableView,
                            HttpEndpointViewSet, OSINTEnableView, OSINTViewSet,
                            TechnologyEnableView, TechnologyViewSet,
                            VulnerabilityEnableView, VulnerabilityViewSet)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('osint', OSINTViewSet)
router.register('hosts', HostViewSet)
router.register('enumeration', EnumerationViewSet),
router.register('endpoints', HttpEndpointViewSet),
router.register('technologies', TechnologyViewSet),
router.register('vulnerabilities', VulnerabilityViewSet),
router.register('exploits', ExploitViewSet)

urlpatterns = [
    path('osint/<int:pk>/enable/', OSINTEnableView.as_view()),
    path('hosts/<int:pk>/enable/', HostEnableView.as_view()),
    path('enumeration/<int:pk>/enable/', EnumerationEnableView.as_view()),
    path('endpoints/<int:pk>/enable/', HttpEndpointEnableView.as_view()),
    path('technologies/<int:pk>/enable/', TechnologyEnableView.as_view()),
    path('vulnerabilities/<int:pk>/enable/', VulnerabilityEnableView.as_view()),
    path('exploits/<int:pk>/enable/', ExploitEnableView.as_view()),
    path('', include(router.urls))
]
