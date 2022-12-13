from typing import Any, Dict

from django.db.models import QuerySet
from targets.views import TargetViewSet

from authentications.filters import AuthenticationFilter
from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer

# Create your views here.


class AuthenticationViewSet(TargetViewSet):

    queryset = Authentication.objects.all().order_by('-id')
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    search_fields = ['name']
    project_members_field = 'target_port__target__project__members'

    def get_project_members(self, data: Dict[str, Any]) -> QuerySet:
        '''Get project members from serializer validated data.

        Args:
            data (Dict[str, Any]): Validated data from serializer

        Returns:
            QuerySet: Project members related to the instance
        '''
        return data['target_port'].target.project.members.all()
