from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from targets.filters import TargetFilter
from targets.models import Target
from targets.serializers import TargetPortSerializer, TargetSerializer

# Create your views here.


class TargetViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_class = TargetFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__members=self.request.user)

    def perform_create(self, serializer):
        project_check = bool(
            self.request.user in serializer.validated_data.get('project').members.all()
        )
        if not project_check:
            raise PermissionDenied()
        super().perform_create(serializer)

    @extend_schema(responses={200: TargetPortSerializer})
    @action(detail=True, methods=['GET'], url_path='ports', url_name='ports')
    def target_ports(self, request, pk):
        target = self.get_object()
        serializer = TargetPortSerializer(target.target_ports.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TargetPortSerializer, responses={201: TargetPortSerializer})
    @target_ports.mapping.post
    def add_target_port(self, request, pk):
        target = self.get_object()
        serializer = TargetPortSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data.copy()
            data['target'] = target
            serializer.create(validated_data=data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['DELETE'],
        url_path='ports/(?P<port_id>[0-9])',
        url_name='delete_port'
    )
    def delete_target_port(self, request, port_id, pk):
        target = self.get_object()
        target_port = get_object_or_404(target.target_ports, pk=port_id)
        target_port.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
