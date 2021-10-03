from django.urls import path
from projects.views import (AddProjectMemberView, DeleteProjectMemberView,
                            ProjectViewSet, TargetViewSet)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('projects', ProjectViewSet)
router.register('targets', TargetViewSet)

urlpatterns = [
    path('projects/<int:pk>/members', AddProjectMemberView.as_view()),
    path('projects/<int:project_pk>/members/<int:member_pk>', DeleteProjectMemberView.as_view())
]
urlpatterns.extend(router.urls)
