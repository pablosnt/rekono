"""Custom permission classes for Django REST Framework authorization.

Implements specialized permission classes for the Rekono platform including
model-level permissions, role-based access control, project membership validation,
and ownership-based authorization. These classes integrate with Django REST Framework
to provide comprehensive security controls for API endpoints.
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
    """Extended Django model permissions with view permission enforcement.

    Extends Django's standard model permissions to include explicit view
    permissions for GET and HEAD requests. This ensures that read operations
    are properly controlled through the permission framework alongside create,
    update, and delete operations.

    Permission Mapping:
        - GET/HEAD: Requires view permission
        - POST: Requires add permission (inherited)
        - PUT/PATCH: Requires change permission (inherited)
        - DELETE: Requires delete permission (inherited)

    Attributes:
        perms_map (dict): Permission mapping for HTTP methods to Django permissions.
    """

    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }


class IsNotAuthenticated(BasePermission):
    """Permission class allowing access only to unauthenticated users.

    Used for endpoints that should only be accessible to anonymous users,
    such as login, registration, or password reset endpoints. Prevents
    authenticated users from accessing these endpoints.

    Use Cases:
        - Login and authentication endpoints
        - User registration forms
        - Password reset requests
        - Public information endpoints
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """Check if the user is not authenticated.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.

        Returns:
            bool: True if user is not authenticated, False otherwise.
        """
        return not request.user.is_authenticated


class IsAdmin(BasePermission):
    """Permission class restricting access to Admin role users only.

    Ensures that only users with the Admin role can access protected endpoints.
    Used for system administration functions, user management, and sensitive
    configuration operations that require the highest level of access.

    Access Control:
        - Only users in the Admin group are granted access
        - All other users, including Auditors and Readers, are denied
        - Unauthenticated requests are automatically denied
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """Check if the user has Admin role.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.

        Returns:
            bool: True if user is an Admin, False otherwise.
        """
        return request.user.groups.filter(name=Role.ADMIN.value).exists()


class IsAuditor(BasePermission):
    """Permission class allowing access to Auditor and Admin role users.

    Implements hierarchical access control where Admin users inherit Auditor
    privileges. Used for security testing operations, findings management,
    and other operational tasks that require elevated privileges.

    Role Hierarchy:
        - Admin: Full access (inherits Auditor privileges)
        - Auditor: Standard access for security operations
        - Reader: No access (denied)
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """Check if the user has Auditor or Admin role.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.

        Returns:
            bool: True if user is an Auditor or Admin, False otherwise.
        """
        return request.user.groups.filter(name__in=[Role.AUDITOR.value, Role.ADMIN.value]).exists()


class ProjectMemberPermission(BasePermission):
    """Permission class enforcing project membership access control.

    Ensures users can only access resources associated with projects they are
    members of. This implements multi-tenant security by isolating project
    data and preventing cross-project data access.

    Features:
        - Project membership validation for object access
        - Support for both single and multiple project associations
        - Automatic approval for objects without project association
        - Multi-tenant security enforcement

    Security Model:
        - Users must be explicit members of the project
        - No access to resources from projects they're not members of
        - Objects without project association are accessible to all authenticated users
    """

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check if user is a member of the object's associated project.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.
            obj (Any): The object being accessed.

        Returns:
            bool: True if user is a project member or object has no project, False otherwise.
        """
        project = obj.parent_project
        if project is None:
            return True
        else:
            projects = [project] if isinstance(project, Project) else project
            return any([p for p in projects if p.members.filter(id=request.user.id).exists()])


class OwnerPermission(BasePermission):
    """Permission class implementing ownership-based access control.

    Enforces ownership permissions where users can only modify resources they own.
    Supports configurable ownership models with customizable owner field mapping
    and admin override capabilities for different model types.

    Security Model:
        - GET requests: Allowed for all authenticated users
        - Modification requests: Only allowed for owners or admins (if enabled)
        - Objects without owners: Accessible to all (with admin override enabled)

    Attributes:
        mapping (dict[Any, dict[str, Any]]): Model-specific ownership configuration mapping.

    Mapping Configuration:
        - instance: Function to determine the actual object to check ownership against
        - owner_field: Name of the field containing the owner reference (default: 'owner')
        - allow_admin: Whether Admin users can bypass ownership checks (default: True)
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
        """Internal method to check ownership permissions.

        Evaluates ownership permissions based on the owner field, admin privileges,
        and request method to determine access rights.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.
            instance (Any): The object instance to check ownership for.
            owner_field (str): The field name containing the owner reference.
            allow_admin (bool): Whether admin users can bypass ownership checks.

        Returns:
            bool: True if access is permitted, False otherwise.
        """
        if not getattr(instance, owner_field):
            allow_admin = True
        return (
            not instance
            or request.method == "GET"
            or (hasattr(instance, owner_field) and getattr(instance, owner_field) == request.user)
            or (allow_admin and IsAdmin().has_permission(request, view))
        )

    def has_permission(self, request: Request, view: View) -> bool:
        """Check permissions for view-level access.

        Special handling for StepViewSet creation to validate ownership of the
        associated Process. This ensures users can only create steps for processes
        they own.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.

        Returns:
            bool: True if access is permitted, False otherwise.
        """
        return (
            self._has_object_permission(
                request, view, Process.objects.get(pk=request.data.get("process_id")), "owner", True
            )
            if view.__class__.__name__ == "StepViewSet" and request.method == "POST"
            else True
        )

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Check ownership permissions for object-level access.

        Uses the configured mapping to determine the appropriate ownership
        validation parameters for the specific object type.

        Args:
            request (Request): The HTTP request object.
            view (View): The view being accessed.
            obj (Any): The specific object being accessed.

        Returns:
            bool: True if access is permitted based on ownership rules, False otherwise.
        """
        return self._has_object_permission(
            request,
            view,
            self.mapping[obj.__class__].get("instance", lambda o: o)(obj),
            self.mapping[obj.__class__].get("owner_field", "owner"),
            self.mapping[obj.__class__].get("allow_admin", True),
        )
