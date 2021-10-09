from django.urls import path, include
from projects.views import (AddProjectMemberView, DeleteProjectMemberView,
                            ProjectViewSet, TargetViewSet, AddTargetPortView, DeleteTargetPortView)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('projects', ProjectViewSet)
router.register('targets', TargetViewSet)

urlpatterns = [
    path('projects/<int:pk>/members/', AddProjectMemberView.as_view()),
    path('projects/<int:pk>/members/<int:member_id>/', DeleteProjectMemberView.as_view()),
    path('targets/<int:pk>/ports/', AddTargetPortView.as_view()),
    path('targets/<int:pk>/ports/<int:port_id>/', DeleteTargetPortView.as_view()),
    path('', include(router.urls))
]
