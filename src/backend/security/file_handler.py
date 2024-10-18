import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any

import magic
from django.core.exceptions import ValidationError
from rekono.settings import CONFIG
from settings.models import Settings

logger = logging.getLogger()


class FileHandler:
    def __init__(
        self,
        extensions: list[str] = ["txt", "text", ""],
        mime_types: list[str] = ["text/plain"],
    ) -> None:
        self.allowed_extensions = extensions
        self.allowed_mime_types = mime_types

    def _validate_size(self, in_memory_file: Any) -> None:
        max_mb_size = Settings.objects.first().max_uploaded_file_mb
        size = in_memory_file.size / (1024 * 1024)  # Get file size in MB
        if size > max_mb_size:  # File size greater than size limit
            logger.warning(
                f"[Security] Attempt of upload too large file with {size} MB"
            )
            raise ValidationError(
                f"File size is greater than the max size allowed ({max_mb_size} MB)",
                code="file",
                params={"value": size},
            )

    def _validate_extension(self, in_memory_file: Any) -> None:
        extension = Path(in_memory_file.name).suffix[1:].lower()  # Get file extension
        if extension not in self.allowed_extensions:
            logger.warning(
                f"[Security] Attempt of upload file with invalid extension: {extension}"
            )
            raise ValidationError(
                "Invalid extension", code="file", params={"value": extension}
            )

    def _validate_mime_type(self, in_memory_file: Any) -> None:
        mime_type = magic.from_buffer(in_memory_file.read(1024), mime=True)
        if mime_type not in self.allowed_mime_types:
            logger.warning(
                f"[Security] Attempt of upload file with invalid MIME type: {mime_type}"
            )
            raise ValidationError(
                "Invalid MIME type", code="file", params={"value": mime_type}
            )

    def validate_file(self, in_memory_file: Any) -> None:
        self._validate_size(in_memory_file)
        self._validate_extension(in_memory_file)
        self._validate_mime_type(in_memory_file)

    def validate_filepath_checksum(self, filepath: str, expected_checksum: str) -> bool:
        with open(filepath, "rb+") as file:
            checksum = hashlib.sha512(file.read()).hexdigest()
            return checksum == expected_checksum

    def store_file(self, in_memory_file: Any) -> tuple[str, str, int]:
        path = CONFIG.wordlists / f"{str(uuid.uuid4())}.txt"
        checksum = hashlib.sha512()
        with path.open("wb+") as stored_file:
            for chunk in in_memory_file.chunks():
                stored_file.write(chunk)
                checksum.update(chunk)
        lines = 0
        with open(path, "rb+") as stored_file:
            lines = len(stored_file.readlines())
        logger.warning(f"[Security] New file uploaded to the server in the path {path}")
        return str(path), str(checksum), lines
