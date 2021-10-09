from executions.views import ExecutionViewSet, TaskViewSet, CancelTaskView
from rest_framework.routers import SimpleRouter
from django.urls import path, include

router = SimpleRouter()
router.register('tasks', TaskViewSet)
router.register('executions', ExecutionViewSet)

urlpatterns = [
    path('tasks/<int:pk>/cancel', CancelTaskView.as_view()),
    path('', include(router.urls))
]
