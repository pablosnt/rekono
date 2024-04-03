from typing import Any, Dict

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)
from users.models import User


class LikeSerializer(ModelSerializer):
    """Common serializer for all models that can be liked."""

    liked = SerializerMethodField(read_only=True)
    likes = SerializerMethodField(read_only=True)

    def get_liked(self, instance: Any) -> bool:
        """Check if an instance is liked by the current user or not.

        Args:
            instance (Any): Instance to check

        Returns:
            bool: Indicate if the current user likes this instance or not
        """
        check_likes = {
            "pk": self.context.get("request").user.id,
            f"liked_{instance.__class__.__name__.lower()}": instance,
        }
        return User.objects.filter(**check_likes).exists()

    def get_likes(self, instance: Any) -> int:
        """Count number of likes for an instance.

        Args:
            instance (Any): Instance to check

        Returns:
            int: Number of likes for this instance
        """
        return instance.liked_by.count()


class MfaSerializer(Serializer):
    mfa = CharField(max_length=200, required=True, write_only=True)
    validator = User.objects.verify_mfa_or_otp

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        if not self.validator(attrs.get("mfa"), self.user if hasattr(self, "user") and getattr(self, "user") else self.context.get("request").user):
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs