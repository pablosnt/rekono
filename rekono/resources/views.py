from api.views import CreateWithUserViewSet
from likes.views import LikeManagementView
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet
from security.authorization.permissions import WordlistCreatorPermission

from resources.filters import WordlistFilter
from resources.models import Wordlist
from resources.serializers import UpdateWordlistSerializer, WordlistSerializer

# Create your views here.


class WordlistViewSet(CreateWithUserViewSet, ModelViewSet, LikeManagementView):
    '''Wordlist ViewSet that includes: get, retrieve, create, update, delete, like and dislike features.'''

    queryset = Wordlist.objects.all().order_by('-id')
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    search_fields = ['name']                                                    # Fields used to search projects
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method
    # Required to include the WordlistCreatorPermission and remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions, WordlistCreatorPermission]
    user_field = 'creator'

    def get_serializer_class(self) -> Serializer:
        '''Get serializer class to use in each request.

        Returns:
            Serializer: Properly serializer to use,
        '''
        if self.request.method == 'PUT':                                        # If PUT request method
            # Use specific serializer for wordlist update
            return UpdateWordlistSerializer
        return super().get_serializer_class()                                   # Otherwise, standard serializer
