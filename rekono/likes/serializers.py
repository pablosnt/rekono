from typing import Any

from rest_framework import serializers
from users.models import User


class LikeBaseSerializer(serializers.Serializer):
    liked = serializers.SerializerMethodField(method_name='is_liked_by_user', read_only=True)
    likes = serializers.SerializerMethodField(method_name='count_likes', read_only=True)

    def is_liked_by_user(self, instance: Any) -> bool:
        check_likes = {
            'pk': self.context.get('request').user.id,
            f'liked_{instance.__class__.__name__.lower()}': instance
        }
        return User.objects.filter(**check_likes).exists()

    def count_likes(self, instance: Any) -> int:
        return instance.liked_by.count()
