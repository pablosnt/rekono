from typing import Any, Dict, List, cast

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from users.models import User


class GetViewSet(GenericViewSet):
    '''Rekono base ViewSet for GET operations.'''

    def get_queryset(self) -> QuerySet:
        '''Get the queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        # Prevent warnings when access the API schema in SwaggerUI or Redoc
        # This is caused by the use of RekonoFilterBackend, that is required for Findings entities
        if self.request.user.id:
            project_filter = {self.members_field: self.request.user}
            return super().get_queryset().filter(**project_filter)
        return None


class CreateWithUserViewSet(GenericViewSet):
    '''Rekono base ViewSet for POST operations with user ownershipt.'''

    def perform_create(self, serializer: Serializer) -> None:
        '''Create a new instance using a serializer and including the user owner.

        Args:
            serializer (Serializer): Serializer to use in the instance creation
        '''
        if self.user_field:
            parameters = {self.user_field: self.request.user}
            serializer.save(**parameters)
        else:
            super().perform_create(serializer)


class CreateViewSet(GenericViewSet):
    '''Rekono base ViewSet for POST operations.'''

    def get_project_members(self, data: Dict[str, Any]) -> List[User]:
        '''Get project members related to the current entity.

        Args:
            data (Dict[str, Any]): Serialized data

        Returns:
            List[User]: List of project members
        '''
        fields = self.members_field.split('__')
        data = data.get(fields[0], {})                                          # Get first serialized field
        for field in fields[1:]:
            data = getattr(data, field)                                         # Get all fields
        return cast(QuerySet, data).all() if data else []                       # Return all members

    def perform_create(self, serializer: Serializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (Serializer): Serializer to use in the instance creation
        '''
        if self.request.user not in self.get_project_members(serializer.validated_data):
            # Current user can't create a new entity in this project
            raise PermissionDenied()
        super().perform_create(serializer)
