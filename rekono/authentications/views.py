from api.views import CreateViewSet, GetViewSet
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)

from authentications.filters import AuthenticationFilter
from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer

# Create your views here.


class AuthenticationViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''Authentication ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = Authentication.objects.all().order_by('-id')
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    search_fields = ['name']
    members_field = 'target_port__target__project__members'
