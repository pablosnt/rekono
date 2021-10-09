from executions.views import ExecutionViewSet, TaskViewSet
from rest_framework.routers import SimpleRouter
from django.urls import path, include

router = SimpleRouter()
router.register('tasks', TaskViewSet)
router.register('executions', ExecutionViewSet)

urlpatterns = [
    path('', include(router.urls))
]
