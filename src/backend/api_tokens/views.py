from api_tokens.filters import ApiTokenFilter
from api_tokens.models import ApiToken
from api_tokens.serializers import ApiTokenSerializer, CreateApiTokenSerializer
from django.db.models import QuerySet
from framework.views import BaseViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

# Create your views here.


class ApiTokenViewSet(BaseViewSet):
    queryset = ApiToken.objects.all()
    serializer_class = ApiTokenSerializer
    filterset_class = ApiTokenFilter
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "expiration"]
    owner_field = "user"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user).all()

    def get_serializer_class(self) -> Serializer:
        if self.request.method == "POST":
            return CreateApiTokenSerializer
        return super().get_serializer_class()
