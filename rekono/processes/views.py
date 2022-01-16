from likes.views import LikeManagementView
from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import (ProcessSerializer, StepPrioritySerializer,
                                   StepSerializer)
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import (ProcessCreatorPermission,
                                                ProjectMemberPermission)

# Create your views here.


class ProcessViewSet(ModelViewSet, LikeManagementView):
    '''Process ViewSet that includes: get, retrieve, create, update, delete, like and dislike features.'''

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    # Fields used to search processes
    search_fields = ['name', 'description', 'steps__tool__name', 'steps__tool__command', 'steps__configuration__name']
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method
    # Required to include the ProcessCreatorPermission to the base authorization classes
    permission_classes = [IsAuthenticated, DjangoModelPermissions, ProjectMemberPermission, ProcessCreatorPermission]

    def perform_create(self, serializer: ProcessSerializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (ProcessSerializer): Serializer to use in the instance creation
        '''
        serializer.save(creator=self.request.user)                              # Include current user as creator


class StepViewSet(ModelViewSet):
    '''Process ViewSet that includes: get, retrieve, create, update and delete features.'''

    queryset = Step.objects.all()
    serializer_class = StepSerializer
    filterset_class = StepFilter
    search_fields = ['tool__name', 'tool__command', 'configuration__name']      # Fields used to search steps
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method
    # Required to include the ProcessCreatorPermission to the base authorization classes
    permission_classes = [IsAuthenticated, DjangoModelPermissions, ProjectMemberPermission, ProcessCreatorPermission]

    def get_serializer_class(self) -> Serializer:
        '''Get serializer class to use in each request.

        Returns:
            Serializer: Properly serializer to use,
        '''
        if self.request.method == 'PUT':                                        # If PUT request method
            # Use specific serializer for priority update
            return StepPrioritySerializer
        return super().get_serializer_class()                                   # Otherwise, standard serializer
