from processes.models import Process, Step
from resources.models import Wordlist
from rest_framework.permissions import BasePermission
from security.authorization.roles import Role


class IsNotAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        admin_group = request.user.groups.filter(name=Role.ADMIN.name.capitalize()).exists()
        return bool(admin_group)


class ProjectMemberPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        project = obj.get_project()
        if project:
            return request.user in project.members.all()
        return True


class BaseCreatorPermission(BasePermission):

    def get_instance(self, obj):
        if self.model and isinstance(obj, self.model):
            return obj

    def has_object_permission(self, request, view, obj):
        instance = self.get_instance(obj)
        if (
            instance
            and request.user.is_authenticated
            and view.action in ['like', 'dislike']
        ):
            return True
        if (
            instance
            and not IsAdmin().has_permission(request, view)
            and request.method in ['POST', 'PUT', 'DELETE']
            and instance.creator != request.user
        ):
            return False
        return True


class ProcessCreatorPermission(BaseCreatorPermission):

    def get_instance(self, obj):
        process = None
        if isinstance(obj, Process):
            process = obj
        elif isinstance(obj, Step):
            process = obj.process
        return process


class WordlistCreatorPermission(BaseCreatorPermission):
    model = Wordlist
