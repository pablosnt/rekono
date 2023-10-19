from typing import Any, Tuple

from platforms.telegram_app.models import TelegramChat
from processes.models import Process, Step
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View
from security.authorization.roles import Role
from wordlists.models import Wordlist


class IsNotAuthenticated(BasePermission):
    """Check if current user is not authenticated."""

    def has_permission(self, request: Request, view: View) -> bool:
        """Check if current user is not authenticated.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        """
        return not request.user.is_authenticated


class IsAdmin(BasePermission):
    """Check if current user is an administrator."""

    def has_permission(self, request: Request, view: View) -> bool:
        """Check if current user is an administrator.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        """
        return request.user.groups.filter(name=str(Role.ADMIN)).exists()


class IsAuditor(BasePermission):
    """Check if current user is an auditor (Admin or Auditor roles)."""

    def has_permission(self, request: Request, view: View) -> bool:
        """Check if current user is an auditor (Admin or Auditor roles).

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        """
        return request.user.groups.filter(
            name__in=[str(Role.AUDITOR), str(Role.ADMIN)]
        ).exists()


class ProjectMemberPermission(BasePermission):
    """Check if current user can access an object based on project membership."""

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check if current user can access some entities based on project membership.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing
            obj (Any): Object that user is accesing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        """
        project = obj.get_project()
        return request.user in project.members.all() or not project


class OwnerPermission(BasePermission):
    """Check if current user can access an object based on HTTP method and creator user."""

    def get_details(self, obj: Any) -> Tuple[Any, str, bool]:  # pragma: no cover
        """Get object with creator user from object accessed by the current user. To be implemented by subclasses.

        Args:
            obj (Any): Object that user is accessing

        Returns:
            Any: Object with creator user
        """
        if obj.__class__ in [Wordlist, Process]:
            return obj, "owner", True
        elif obj.__class__ == Step:
            return obj.process, "owner", True
        elif obj.__class__ == TelegramChat:
            return obj, "user", "False"

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check if current user can access an object based on HTTP method and creator user.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing
            obj (Any): Object that user is accesing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        """
        instance, field, allow_admin = self.get_details(obj)
        return (
            not instance
            or request.method == "GET"
            or getattr(instance, field) == request.user
            or (allow_admin and IsAdmin().has_permission(request, view))
        )
