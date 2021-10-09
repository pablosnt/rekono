from processes.models import Process, Step
from processes.serializers import (ProcessSerializer, StepPrioritySerializer,
                                   StepSerializer)
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

# Create your views here.


class ProcessViewSet(ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_fields = {
        'name': ['exact', 'contains'],
        'description': ['exact', 'contains'],
        'creator': ['exact'],
    }
    http_method_names = ['get', 'post', 'put', 'delete']

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class StepViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
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


class UpdateStepViewSet(GenericViewSet, UpdateModelMixin):
    queryset = Step.objects.all()
    serializer_class = StepPrioritySerializer
