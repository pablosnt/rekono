from typing import Any

from platforms.telegram_app.models import TelegramChat
from processes.models import Process, Step
from rest_framework.permissions import BasePermission, DjangoModelPermissions
from rest_framework.request import Request
from rest_framework.views import View
from security.authorization.roles import Role
from wordlists.models import Wordlist
from notes.models import Note


class RekonoModelPermission(DjangoModelPermissions):
    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }


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
        return not project or request.user in project.members.all()


class OwnerPermission(BasePermission):
    """Check if current user can access an object based on HTTP method and creator user."""

    def _has_object_permission(
        self,
        request: Request,
        instance: Any,
        owner_field: str,
        allow_admin: bool,
    ) -> bool:
        if not getattr(instance, owner_field):
            allow_admin = True
        return (
            not instance
            or request.method == "GET"
            or (
                request.method == "POST"
                and "/fork/" in request.path
                and isinstance(instance, Note)
            )
            or (
                hasattr(instance, owner_field)
                and getattr(instance, owner_field) == request.user
            )
            or (allow_admin and IsAdmin().has_permission(request, owner_field))
        )

    def has_permission(self, request: Request, view: View) -> bool:
        return (
            self._has_object_permission(
                request,
                Process.objects.get(pk=request.data.get("process_id")),
                "owner",
                True,
            )
            if view.__class__.__name__ == "StepViewSet" and request.method == "POST"
            else True
        )

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check if current user can access an object based on HTTP method and creator user.

        Args:
            request (Request): HTTP request
            view (View): View that user is accessing
            obj (Any): Object that user is accesing

        Returns:
            bool: Indicate if user is authorized to make this request or not
        """
        instance = None
        owner_field = ""
        allow_admin = False
        if obj.__class__ in [Wordlist, Process, Step, Note]:
            instance = obj.process if obj.__class__ == Step else obj
            owner_field = "owner"
            allow_admin = not isinstance(obj, Note)
        elif obj.__class__ == TelegramChat:
            instance = obj
            owner_field = "user"
        return self._has_object_permission(request, instance, owner_field, allow_admin)
