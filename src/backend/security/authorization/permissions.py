from typing import Any

from rest_framework.permissions import BasePermission, DjangoModelPermissions
from rest_framework.request import Request
from rest_framework.views import View

from alerts.models import Alert
from notes.models import Note
from platforms.telegram_app.models import TelegramChat
from processes.models import Process, Step
from projects.models import Project
from reporting.models import Report
from security.authorization.roles import Role
from wordlists.models import Wordlist


class RekonoModelPermission(DjangoModelPermissions):
    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return not request.user.is_authenticated


class IsAdmin(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return request.user.groups.filter(name=Role.ADMIN.value).exists()


class IsAuditor(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return request.user.groups.filter(name__in=[Role.AUDITOR.value, Role.ADMIN.value]).exists()


class ProjectMemberPermission(BasePermission):
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        project = obj.parent_project
        if project is None:
            return True
        else:
            projects = [project] if isinstance(project, Project) else project
            return any([p for p in projects if p.members.filter(id=request.user.id).exists()])


class OwnerPermission(BasePermission):
    # By default: instance returns the same object, allow_admin is True and owner_field is owner
    mapping: dict[Any, dict[str, Any]] = {
        Wordlist: {},
        Process: {},
        Step: {"instance": lambda o: o.process},
        Note: {"allow_admin": False},
        Alert: {},
        TelegramChat: {"owner_field": "user", "allow_admin": False},
        Report: {"owner_field": "user"},
    }

    def _has_object_permission(
        self, request: Request, view: View, instance: Any, owner_field: str, allow_admin: bool
    ) -> bool:
        if not getattr(instance, owner_field):
            allow_admin = True
        return (
            not instance
            or request.method == "GET"
            or (hasattr(instance, owner_field) and getattr(instance, owner_field) == request.user)
            or (allow_admin and IsAdmin().has_permission(request, view))
        )

    def has_permission(self, request: Request, view: View) -> bool:
        return (
            self._has_object_permission(
                request, view, Process.objects.get(pk=request.data.get("process_id")), "owner", True
            )
            if view.__class__.__name__ == "StepViewSet" and request.method == "POST"
            else True
        )

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        return self._has_object_permission(
            request,
            view,
            self.mapping[obj.__class__].get("instance", lambda o: o)(obj),
            self.mapping[obj.__class__].get("owner_field", "owner"),
            self.mapping[obj.__class__].get("allow_admin", True),
        )
