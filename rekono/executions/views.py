from drf_spectacular.utils import extend_schema
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from integrations.defect_dojo import executions as dd_uploader
from integrations.defect_dojo.exceptions import (EngagementIdNotFoundException,
                                                 ProductIdNotFoundException)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class ExecutionViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    filterset_fields = {
        'task': ['exact'],
        'task__target': ['exact'],
        'task__target__project': ['exact'],
        'task__process': ['exact'],
        'task__tool': ['exact'],
        'task__intensity': ['exact'],
        'task__executor': ['exact'],
        'status': ['exact'],
        'step__tool': ['exact'],
        'start': ['gte', 'lte', 'exact'],
        'end': ['gte', 'lte', 'exact']
    }
    ordering_fields = (
        ('target', 'task__target'),
        ('project', 'task__target__project'),
        ('process', 'task__process'),
        ('intensity', 'task__intensity'),
        ('executor', 'task__executor'),
        'task__tool', 'step_tool',
        'status', 'start', 'end'
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user).order_by('-id')

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo(self, request, pk):
        execution = self.get_object()
        try:
            dd_uploader.upload([execution])
            return Response(status=status.HTTP_200_OK)
        except (ProductIdNotFoundException, EngagementIdNotFoundException) as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
