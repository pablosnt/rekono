"""Django REST framework serializers for wordlist models.

Provides serializer classes for wordlist file upload, validation, and conversion
between Django model instances and JSON data. Includes file handling capabilities
and secure storage with integrity validation.
"""

from typing import Any

from rest_framework.serializers import FileField, ModelSerializer

from framework.serializers import LikeSerializer
from rekono.settings import CONFIG
from security.file_handler import FileHandler
from users.serializers import SimpleUserSerializer
from wordlists.models import Wordlist


class WordlistSerializer(LikeSerializer):
    """Serializer for Wordlist model with file upload capabilities.

    Handles serialization of Wordlist instances including secure file upload,
    validation, and automatic file processing. Integrates with like functionality
    and user ownership management.

    Attributes:
        file (FileField): Wordlist content submitted for upload (write-only)
        owner (SimpleUserSerializer): Serialized user information for wordlist owner
    """

    file = FileField(required=True, allow_empty_file=False, write_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the WordlistSerializer.

        Attributes:
            model (Model): The Wordlist model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

        model = Wordlist
        fields = ("id", "name", "type", "file", "size", "owner", "liked", "likes")
        read_only_fields = ("size", "owner", "liked", "likes")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate uploaded wordlist file.

        Performs security validation on the uploaded file to ensure it meets
        safety requirements before processing and storage.

        Args:
            attrs (dict[str, Any]): The attributes to validate

        Returns:
            dict[str, Any]: The validated attributes

        Raises:
            ValidationError: If file validation fails
        """
        attrs = super().validate(attrs)  # Run standard attribute validation before the file-specific security checks
        FileHandler().validate_file(attrs["file"])
        return attrs

    def save(self, **kwargs: Any) -> Wordlist:
        """Save the wordlist with secure file handling.

        Processes the uploaded file, calculates checksum, determines size,
        and stores it securely in the configured wordlists directory.

        Args:
            **kwargs (Any): Additional keyword arguments for saving

        Returns:
            Wordlist: The created Wordlist instance with file metadata
        """
        (
            self.validated_data["path"],
            self.validated_data["checksum"],
            self.validated_data["size"],
        ) = FileHandler().store_file(CONFIG.wordlists, self.validated_data.pop("file"))
        return super().save(**kwargs)


class UpdateWordlistSerializer(ModelSerializer):
    """Serializer for updating existing wordlist metadata.

    Specialized version of the wordlist serializer that only allows modification
    of metadata fields, not the file itself. Used for wordlist updates.
    """

    class Meta:
        """Meta configuration for the UpdateWordlistSerializer.

        Attributes:
            model (Model): The Wordlist model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = Wordlist
        fields = ("id", "name", "type")
