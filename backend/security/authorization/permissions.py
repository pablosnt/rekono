"""Permission classes that DRF combines to authorize the API requests.

Besides the model permissions given by the role of the user, the access to an
object also depends on the project it belongs to and, for the personal resources,
on the user that owns it.
"""

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
    """Model permissions that also require the view permission to read.

    Django only checks the model permissions of the write methods, so the read
    ones are added here to let the roles decide which models each user can see.

    Attributes:
        perms_map: Model permission required by each HTTP method.
    """

    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }


class IsNotAuthenticated(BasePermission):
    """Access granted only to the anonymous users, like in the login endpoints."""

    def has_permission(self, request: Request, view: View) -> bool:
        """Check that the request doesn't come from an authenticated user.

        Args:
            request: Request whose authentication is checked.
            view: View that handles the request, not used to grant the access.

        Returns:
            Whether the request is anonymous.
        """
        return not request.user.is_authenticated


class IsAdmin(BasePermission):
    """Access granted only to the users with the Admin role."""

    def has_permission(self, request: Request, view: View) -> bool:
        """Check that the user has the Admin role.

        Args:
            request: Request whose user roles are checked.
            view: View that handles the request, not used to grant the access.

        Returns:
            Whether the user has the Admin role.
        """
        return request.user.groups.filter(name=Role.ADMIN.value).exists()


class IsAuditor(BasePermission):
    """Access granted to the users with the Auditor or the Admin role."""

    def has_permission(self, request: Request, view: View) -> bool:
        """Check that the user has the Auditor or the Admin role.

        Args:
            request: Request whose user roles are checked.
            view: View that handles the request, not used to grant the access.

        Returns:
            Whether the user has any of those two roles.
        """
        return request.user.groups.filter(name__in=[Role.AUDITOR.value, Role.ADMIN.value]).exists()


class ProjectMemberPermission(BasePermission):
    """Access granted only to the members of the project that an object belongs to."""

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check that the user is a member of the project that the object belongs to.

        Objects related to several projects are accessible if the user is a member
        of any of them.

        Args:
            request: Request whose user is checked against the membership.
            view: View that handles the request, not used to grant the access.
            obj: Object to be accessed, which must expose a parent_project holding
              one project, several of them, or None for the global objects.

        Returns:
            Whether the user can access the object. True for the global objects,
            whose access is only controlled by the permissions of the user.
        """
        project = obj.parent_project
        if project is None:
            # obj.parent_project is None for models that aren't scoped to a single
            # project (global objects), so there is no membership to check here
            return True
        else:
            projects = [project] if isinstance(project, Project) else project
            return any([p for p in projects if p.members.filter(id=request.user.id).exists()])


class OwnerPermission(BasePermission):
    """Access to modify the personal resources granted only to the user that owns them.

    Attributes:
        mapping: Ownership configuration of each model that has an owner. The
          ``instance`` entry gets the object whose owner decides, ``owner_field``
          names the field that references the owner, and ``allow_admin`` tells if
          the administrators can modify the resources of other users.
    """

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
        """Check if the user can modify an object, according to its ownership.

        Args:
            request: Request to be authorized.
            view: View that handles the request.
            instance: Object whose owner decides if the request is authorized.
            owner_field: Field that references the owner of the object.
            allow_admin: Whether the administrators can modify this object even if
              they don't own it.

        Returns:
            Whether the request is authorized. Always True for the read requests,
            since the ownership only restricts the modifications.
        """
        # An object without owner can always be managed by the administrators, since
        # otherwise nobody could manage it
        if not getattr(instance, owner_field):
            allow_admin = True
        return (
            not instance
            or request.method == "GET"
            or (hasattr(instance, owner_field) and getattr(instance, owner_field) == request.user)
            or (allow_admin and IsAdmin().has_permission(request, view))
        )

    def has_permission(self, request: Request, view: View) -> bool:
        """Check that a new step is created in a process owned by the user.

        Creating a step is the only case that can't be authorized by the object
        permissions, because the object doesn't exist yet and its ownership comes
        from the process that will contain it.

        Args:
            request: Request whose body provides the process_id when a step is
              being created.
            view: View that handles the request, matched by class name, since the
              step creation is the only case checked here.

        Returns:
            Whether the request is authorized. True for every other request, which
            is authorized by the object permissions instead.
        """
        return (
            self._has_object_permission(
                request, view, Process.objects.get(pk=request.data.get("process_id")), "owner", True
            )
            if view.__class__.__name__ == "StepViewSet" and request.method == "POST"
            else True
        )

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check that the user can modify an object, using its model configuration.

        Args:
            request: Request whose user is compared against the object owner.
            view: View that handles the request, forwarded to the admin check.
            obj: Object to be accessed, whose model must be one of the keys of the
              mapping, since that is where its owner field is configured.

        Returns:
            Whether the user can modify the object.
        """
        return self._has_object_permission(
            request,
            view,
            self.mapping[obj.__class__].get("instance", lambda o: o)(obj),
            self.mapping[obj.__class__].get("owner_field", "owner"),
            self.mapping[obj.__class__].get("allow_admin", True),
        )
