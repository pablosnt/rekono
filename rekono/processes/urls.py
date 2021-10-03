from processes.views import ProcessViewSet, StepViewSet, UpdateStepViewSet
from rest_framework.routers import SimpleRouter
from django.urls import path, include

router = SimpleRouter()
router.register('processes', ProcessViewSet)
router.register('steps', StepViewSet)

urlpatterns = [
    path('steps/<int:pk>/', UpdateStepViewSet.as_view({'put': 'update'})),
    path('', include(router.urls))
]
