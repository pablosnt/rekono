from executions.views import ExecutionViewSet, RequestViewSet, CancelRequestView
from rest_framework.routers import SimpleRouter
from django.urls import path, include

router = SimpleRouter()
router.register('requests', RequestViewSet)
router.register('executions', ExecutionViewSet)

urlpatterns = [
    path('requests/<int:pk>/cancel', CancelRequestView.as_view()),
    path('', include(router.urls))
]
