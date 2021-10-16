from rest_framework.permissions import BasePermission
from security.authorization.roles import Role

from processes.models import Process, Step


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


class ProcessCreatorPermission(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        process = None
        if isinstance(obj, Process):
            process = obj
        elif isinstance(obj, Step):
            process = obj.process
        if (
            process and
            not IsAdmin().has_permission(request, view) and
            request.method in ['POST', 'PUT', 'DELETE'] and
            process.creator != request.user
        ):
            return False
        return True
