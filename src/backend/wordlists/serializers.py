import os
import uuid
from typing import Any, Dict

from rekono.settings import CONFIG
from rest_framework import serializers
from security.file_handler import FileHandler

# from likes.serializers import LikeBaseSerializer
from wordlists.models import Wordlist

# from users.serializers import SimplyUserSerializer


# LikeBaseSerializer
class WordlistSerializer(serializers.ModelSerializer):
    """Serializer to manage wordlists via API."""

    # Wordlist file, to allow the wordlist files upload to the server
    file = serializers.FileField(required=True, allow_empty_file=False, write_only=True)
    # creator = SimplyUserSerializer(many=False, read_only=True)                  # Creator details for read operations

    class Meta:
        model = Wordlist
        # Wordlist fields exposed via API
        fields = (
            "id",
            "name",
            "type",
            "path",
            "file",
            "checksum",
            "size",
            # "creator",
            # "liked",
            # "likes",
        )
        # read_only_fields = ("creator",)  # Read only field
        # Parameters used in write operations, but they will be generated automatically from uploaded file
        extra_kwargs = {
            "path": {"write_only": True, "required": False},
            "checksum": {"write_only": True, "required": False},
        }

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


class UpdateWordlistSerializer(serializers.ModelSerializer):
    """Serializer to update wordlists via API."""

    class Meta:
        """Serializer metadata."""

        model = Wordlist
        fields = ("id", "name", "type")  # Wordlist fields exposed via API
