from django.core.exceptions import PermissionDenied
from processes.models import Process, Step
from processes.serializers import (ProcessSerializer, StepPrioritySerializer,
                                   StepSerializer)
from rest_framework.viewsets import ModelViewSet
from authorization.permissions import IsAdmin

# Create your views here.


class ProcessViewSet(ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_fields = {
        'name': ['exact', 'contains'],
        'description': ['exact', 'contains'],
        'creator': ['exact'],
    }
    ordering_fields = ('name', 'creator')
    http_method_names = ['get', 'post', 'put', 'delete']

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class StepViewSet(ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    filterset_fields = {
        'process__name': ['exact', 'contains'],
        'process__description': ['exact', 'contains'],
        'process__creator': ['exact'],
        'tool': ['exact'],
        'configuration': ['exact'],
        'priority': ['exact'],
    }
    ordering_fields = ('process', 'tool', 'configuration', 'priority')

    def perform_create(self, serializer):
        process_check = bool(
            serializer.validated_data.get('process').creator == self.request.user or
            IsAdmin().has_permission(self.request, self)
        )
        if not process_check:
            raise PermissionDenied()
        super().perform_create(serializer)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return StepPrioritySerializer
        return super().get_serializer_class()
