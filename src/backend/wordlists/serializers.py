from typing import Any, Dict

from framework.serializers import LikeSerializer
from rekono.settings import CONFIG
from rest_framework.serializers import FileField, ModelSerializer
from security.utils.file_handler import FileHandler
from users.serializers import SimpleUserSerializer
from wordlists.models import Wordlist


class WordlistSerializer(ModelSerializer, LikeSerializer):
    """Serializer to manage wordlists via API."""

    # Wordlist file, to allow the wordlist files upload to the server
    file = FileField(required=True, allow_empty_file=False, write_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Wordlist
        # Wordlist fields exposed via API
        fields = (
            "id",
            "name",
            "type",
            "file",
            "size",
            "owner",
            "liked",
            "likes",
        )
        read_only_fields = ("size", "owner", "liked", "likes")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Returns:
            Dict[str, Any]: Data after validation process
        """
        attrs = super().validate(attrs)  # Original data validation
        FileHandler().validate_file(attrs["file"])
        return attrs

    def save(self, **kwargs: Any) -> Wordlist:
        """Save changes in instance.

        Returns:
            Wordlist: Instance after apply changes
        """
        (
            self.validated_data["path"],
            self.validated_data["checksum"],
            self.validated_data["size"],
        ) = FileHandler().store_file(self.validated_data.pop("file"))
        return super().save(**kwargs)


class UpdateWordlistSerializer(ModelSerializer):
    """Serializer to update wordlists via API."""

    class Meta:
        """Serializer metadata."""

        model = Wordlist
        fields = ("id", "name", "type")  # Wordlist fields exposed via API