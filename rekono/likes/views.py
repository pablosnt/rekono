from django.db.models import Count, QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from security.authorization.permissions import IsAuditor
from users.models import User

# Create your views here.


class LikeManagementView(GenericViewSet):
    '''Base ViewSet that includes the like and dislike features.'''

    def get_queryset(self) -> QuerySet:
        '''Get the model queryset. It's required for allow the access to the likes count by the child ViewSets.

        Returns:
            QuerySet: Model queryset
        '''
        return super().get_queryset().annotate(likes_count=Count('liked_by'))

    @extend_schema(request=None, responses={201: None})
    # Permission classes are overrided to IsAuthenticated and IsAuditor, because currently only Tools, Processes and
    # Resources (Wordlists) can be liked, and auditors and admins are the only ones that can see this resources.
    # Permission classes should be overrided here, because if not, the standard permissions would be applied, and not
    # all auditors can make POST requests to resources like these.
    @action(
        detail=True,
        methods=['POST'],
        url_path='like',
        url_name='like',
        permission_classes=[IsAuthenticated, IsAuditor]
    )
    def like(self, request: Request, pk: str) -> Response:
        '''Mark an instance as liked by the current user.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        instance = self.get_object()
        instance.liked_by.add(request.user)                                     # Add user like
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={204: None})
    # Permission classes is overrided to IsAuthenticated and IsAuditor, because currently only Tools, Processes and
    # Resources (Wordlists) can be liked, and auditors and admins are the only ones that can see this resources.
    # Permission classes should be overrided here, because if not, the standard permissions would be applied, and not
    # all auditors can make POST requests to resources like these.
    @action(
        detail=True,
        methods=['POST'],
        url_path='dislike',
        url_name='dislike',
        permission_classes=[IsAuthenticated, IsAuditor]
    )
    def dislike(self, request: Request, pk: str) -> Response:
        '''Unmark an instance as liked by the current user.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        instance = self.get_object()
        user: User = request.user
        instance.liked_by.remove(user)                                          # Remove user like
        # Remove instance from liked instances by user
        getattr(user, f'liked_{instance.__class__.__name__.lower()}').remove(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
