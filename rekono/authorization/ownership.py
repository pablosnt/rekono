from rest_framework.permissions import BasePermission
from authorization.groups.roles import Role

from processes.models import Process, Step


class RekonoOwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        process = None
        project = obj.get_project()
        if project:
            return request.user in project.members.all()
        if isinstance(obj, Process):
            process = obj
        elif isinstance(obj, Step):
            process = obj.process
        if process:
            admin_group = request.user.groups.filter(name=Role.ADMIN.name.capitalize()).exists()
            if (
                not admin_group and
                request.http_method in ['POST', 'PUT', 'DELETE'] and
                process.creator != request.user
            ):
                return False
        return True
