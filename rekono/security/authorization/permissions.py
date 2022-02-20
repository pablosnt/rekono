from typing import Any

from processes.models import Process, Step
from resources.models import Wordlist
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View
from security.authorization.roles import Role


class IsNotAuthenticated(BasePermission):
    '''Check if current user is not authenticated.'''

    def has_permission(self, request: Request, view: View) -> bool:
        '''Check if current user is not authenticated.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        '''
        return not request.user.is_authenticated


class IsAdmin(BasePermission):
    '''Check if current user is an administrator.'''

    def has_permission(self, request: Request, view: View) -> bool:
        '''Check if current user is an administrator.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        '''
        return bool(request.user.groups.filter(name=str(Role.ADMIN)).exists())


class IsAuditor(BasePermission):
    '''Check if current user is an auditor (Admin or Auditor roles).'''

    def has_permission(self, request: Request, view: View) -> bool:
        '''Check if current user is an auditor (Admin or Auditor roles).

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        '''
        return (
            bool(request.user.groups.filter(name=str(Role.AUDITOR)).exists()) or
            IsAdmin().has_permission(request, view)
        )


class ProjectMemberPermission(BasePermission):
    '''Check if current user can access an object based on project membership.'''

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        '''Check if current user can access some entities based on project membership.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing
            obj (Any): Object that user is accesing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        '''
        # Check if current user is a project member
        return request.user in obj.get_project().members.all()


class BaseCreatorPermission(BasePermission):
    '''Check if current user can access an object based on HTTP method and creator user.'''

    def get_instance(self, obj: Any) -> Any:                                    # pragma: no cover
        '''Get object with creator user from object accessed by the current user. To be implemented by subclasses.

        Args:
            obj (Any): Object that user is accessing

        Returns:
            Any: Object with creator user
        '''
        pass

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        '''Check if current user can access an object based on HTTP method and creator user.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing
            obj (Any): Object that user is accesing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        '''
        instance = self.get_instance(obj)                                       # Get object with creator user
        if (
            instance and                                                        # Instance exists
            not IsAdmin().has_permission(request, view) and                     # Non admin users
            request.method in ['POST', 'PUT', 'DELETE'] and                     # Write operations
            instance.creator != request.user                                    # Non creator user
        ):
            return False                                                        # Access denied
        return True


class ProcessCreatorPermission(BaseCreatorPermission):
    '''Check if current user can access a Process or Step based on HTTP method and creator user.'''

    def get_instance(self, obj: Any) -> Any:
        '''Get object with creator user from object accessed by the current user.

        Args:
            obj (Any): Object that user is accessing

        Returns:
            Any: Object with creator user
        '''
        if isinstance(obj, Process):
            return obj
        return obj.process if isinstance(obj, Step) else None


class WordlistCreatorPermission(BaseCreatorPermission):
    '''Check if current user can access a Wordlist based on HTTP method and creator user.'''

    def get_instance(self, obj: Any) -> Any:
        '''Get object with creator user from object accessed by the current user.

        Args:
            obj (Any): Object that user is accessing

        Returns:
            Any: Object with creator user
        '''
        return obj if isinstance(obj, Wordlist) else None
