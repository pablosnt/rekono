from authentications.filters import AuthenticationFilter
from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer
from framework.views import BaseViewSet

# Create your views here.


class AuthenticationViewSet(BaseViewSet):
    """Authentication ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = Authentication.objects.all()
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    search_fields = ["name"]
    ordering_fields = ["id", "target_port", "name", "type"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

    # members_field = "target_port__target__project__members"
