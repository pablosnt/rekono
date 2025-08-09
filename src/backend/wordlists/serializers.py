from typing import Any

from rest_framework.serializers import FileField, ModelSerializer

from framework.serializers import LikeSerializer
from rekono.settings import CONFIG
from security.file_handler import FileHandler
from users.serializers import SimpleUserSerializer
from wordlists.models import Wordlist


class WordlistSerializer(LikeSerializer):
    # Wordlist file, to allow the wordlist files upload to the server
    file = FileField(required=True, allow_empty_file=False, write_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Wordlist
        # Wordlist fields exposed via API
        fields = ("id", "name", "type", "file", "size", "owner", "liked", "likes")
        read_only_fields = ("size", "owner", "liked", "likes")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)  # Original data validation
        FileHandler().validate_file(attrs["file"])
        return attrs

    def save(self, **kwargs: Any) -> Wordlist:
        (
            self.validated_data["path"],
            self.validated_data["checksum"],
            self.validated_data["size"],
        ) = FileHandler().store_file(CONFIG.wordlists, self.validated_data.pop("file"))
        return super().save(**kwargs)


class UpdateWordlistSerializer(ModelSerializer):
    class Meta:
        model = Wordlist
        fields = ("id", "name", "type")
