from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import (ProcessSerializer, StepPrioritySerializer,
                                   StepSerializer)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import (ProcessCreatorPermission,
                                                ProjectMemberPermission)

# Create your views here.


class ProcessViewSet(ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [
        IsAuthenticated, DjangoModelPermissions, ProjectMemberPermission, ProcessCreatorPermission
    ]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class StepViewSet(ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    filterset_class = StepFilter
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [
        IsAuthenticated, DjangoModelPermissions, ProjectMemberPermission, ProcessCreatorPermission
    ]

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return StepPrioritySerializer
        return super().get_serializer_class()
