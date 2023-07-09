from typing import Any

from rest_framework import serializers
from users.models import User


class LikeBaseSerializer(serializers.Serializer):
    '''Common serializer for all models that can be liked.'''

    # Field that indicates if the current user likes or not each entity
    liked = serializers.SerializerMethodField(method_name='is_liked_by_user', read_only=True)
    # Field that indicates the number of likes for each entity
    likes = serializers.SerializerMethodField(method_name='count_likes', read_only=True)

    def is_liked_by_user(self, instance: Any) -> bool:
        '''Check if an instance is liked by the current user or not.

        Args:
            instance (Any): Instance to check

        Returns:
            bool: Indicate if the current user likes this instance or not
        '''
        check_likes = {                                                         # Filter users by Id and liked entities
            'pk': self.context.get('request').user.id,
            f'liked_{instance.__class__.__name__.lower()}': instance
        }
        return User.objects.filter(**check_likes).exists()

    def count_likes(self, instance: Any) -> int:
        '''Count number of likes for an instance.

        Args:
            instance (Any): Instance to check

        Returns:
            int: Number of likes for this instance
        '''
        return instance.liked_by.count()
