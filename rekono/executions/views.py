from executions.exceptions import InvalidRequestException
from rest_framework.views import APIView
from executions.models import Execution, Request
from executions.serializers import ExecutionSerializer, RequestSerializer
from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from executions import services

# Create your views here.


class RequestViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)


class ExecutionViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer


class CancelRequestView(APIView):

    def post(self, request, pk, format=None):
        try:
            req = Request.objects.get(pk=pk)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            services.cancel_request(req)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvalidRequestException:
            return Response(status=status.HTTP_400_BAD_REQUEST)
