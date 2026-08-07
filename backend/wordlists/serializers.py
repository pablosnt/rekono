"""Serializers of the wordlist endpoints."""

from typing import Any

from rest_framework.serializers import FileField, ModelSerializer

from framework.serializers import LikeSerializer
from rekono.settings import CONFIG
from security.file_handler import FileHandler
from users.serializers import SimpleUserSerializer
from wordlists.models import Wordlist


class WordlistSerializer(LikeSerializer):
    """Serializer of a wordlist, including the file with its content.

    Attributes:
        file: Content of the wordlist, which is stored in the file system instead
          of in the database, so it's only used to create the wordlist.
        owner: User that uploaded the wordlist.
    """

    file = FileField(required=True, allow_empty_file=False, write_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the wordlists."""

        model = Wordlist
        fields = ("id", "name", "type", "file", "size", "owner", "liked", "likes")
        read_only_fields = ("size", "owner", "liked", "likes")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the uploaded file is safe to store.

        Args:
            attrs: Wordlist fields sent by the user, including the uploaded file.

        Returns:
            The same validated data, unchanged.

        Raises:
            ValidationError: If the file is too large, or its extension or MIME type
              isn't accepted.
        """
        attrs = super().validate(attrs)
        FileHandler().validate_file(attrs["file"])
        return attrs

    def save(self, **kwargs: Any) -> Wordlist:
        """Store the uploaded file and save the wordlist that points to it.

        Args:
            **kwargs: Extra fields for the wordlist, like the owner that the viewset
              adds.

        Returns:
            The saved wordlist, with the path, the checksum, and the size that the
            stored file has, since none of them are provided by the user.
        """
        (
            self.validated_data["path"],
            self.validated_data["checksum"],
            self.validated_data["size"],
        ) = FileHandler().store_file(CONFIG.wordlists, self.validated_data.pop("file"))
        return super().save(**kwargs)


class UpdateWordlistSerializer(ModelSerializer):
    """Serializer of the wordlist data that can be updated after the upload.

    The file can't be replaced, since the executions that used the wordlist would
    stop matching the content that they actually ran against.
    """

    class Meta:
        """Serializer configuration for the wordlist updates."""

        model = Wordlist
        fields = ("id", "name", "type")
