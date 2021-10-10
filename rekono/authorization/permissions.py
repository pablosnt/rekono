from rest_framework.permissions import BasePermission
from authorization.groups.roles import Role

from processes.models import Process, Step


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
        if process:
            admin_group = request.user.groups.filter(name=Role.ADMIN.name.capitalize()).exists()
            if (
                not admin_group and
                request.method in ['POST', 'PUT', 'DELETE'] and
                process.creator != request.user
            ):
                return False
        return True


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        admin_group = request.user.groups.filter(name=Role.ADMIN.name.capitalize()).exists()
        return bool(admin_group)
