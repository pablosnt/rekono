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
    '''Wordlist ViewSet that includes: get, retrieve, create, update, delete, like and dislike features.'''

    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    search_fields = ['name']                                                    # Fields used to search projects
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method
    # Required to include the WordlistCreatorPermission to the base authorization classes
    permission_classes = [IsAuthenticated, DjangoModelPermissions, ProjectMemberPermission, WordlistCreatorPermission]

    def perform_create(self, serializer: WordlistSerializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (WordlistSerializer): Serializer to use in the instance creation
        '''
        serializer.save(creator=self.request.user)                              # Include current user as creator
