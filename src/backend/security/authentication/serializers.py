import logging
from typing import Any, Dict

from platforms.mail.notifications import SMTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from security.authorization.roles import Role
from users.models import User

logger = logging.getLogger()


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        User.objects.invalidate_all_tokens(self.user, exclude_latest=True)
        SMTP().login_notification(self.user)
        logger.info(
            f"[Security] User {self.user.id} has logged in",
            extra={"user": self.user.id},
        )
        return attrs

    @classmethod
    def get_token(cls, user: User) -> Dict[str, Any]:
        token = super().get_token(user)
        group = user.groups.first()
        token["role"] = group.name if group else Role.READER.value
        return token
