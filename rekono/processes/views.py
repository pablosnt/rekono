from django.core.exceptions import PermissionDenied
from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import (ProcessSerializer, StepPrioritySerializer,
                                   StepSerializer)
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import IsAdmin

# Create your views here.


class ProcessViewSet(ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class StepViewSet(ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    filterset_class = StepFilter

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
