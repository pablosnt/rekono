from likes.views import LikeManagementView
from resources.filters import WordlistFilter
from resources.models import Wordlist
from resources.serializers import WordlistSerializer
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import (ProjectMemberPermission,
                                                WordlistCreatorPermission)

# Create your views here.


class WordlistViewSet(ModelViewSet, LikeManagementView):
    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    search_fields = ['name']
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [
        IsAuthenticated, DjangoModelPermissions, ProjectMemberPermission, WordlistCreatorPermission
    ]

    def perform_create(self, serializer):
        serializer.validated_data['creator'] = self.request.user
        serializer.save()
