from api.views import CreateWithUserViewSet
from likes.views import LikeManagementView
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import ProcessCreatorPermission

from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import (ProcessSerializer, StepPrioritySerializer,
                                   StepSerializer)

# Create your views here.


class ProcessViewSet(CreateWithUserViewSet, ModelViewSet, LikeManagementView):
    '''Process ViewSet that includes: get, retrieve, create, update, delete, like and dislike features.'''

    queryset = Process.objects.all().order_by('-id')
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    # Fields used to search processes
    search_fields = ['name', 'description']
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method
    # Required to include the ProcessCreatorPermission and remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions, ProcessCreatorPermission]
    user_field = 'creator'


class StepViewSet(ModelViewSet):
    '''Step ViewSet that includes: get, retrieve, create, update and delete features.'''

    queryset = Step.objects.all().order_by('-id')
    serializer_class = StepSerializer
    filterset_class = StepFilter
    search_fields = ['tool__name', 'tool__command', 'configuration__name']      # Fields used to search steps
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method
    # Required to include the ProcessCreatorPermission and remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions, ProcessCreatorPermission]

    def get_serializer_class(self) -> Serializer:
        '''Get serializer class to use in each request.

        Returns:
            Serializer: Properly serializer to use,
        '''
        if self.request.method == 'PUT':                                        # If PUT request method
            # Use specific serializer for priority update
            return StepPrioritySerializer
        return super().get_serializer_class()                                   # Otherwise, standard serializer
