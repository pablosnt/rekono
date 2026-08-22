"""Validation and storage of the files uploaded by the users."""

import hashlib
import uuid
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import magic
from django.core.exceptions import ValidationError

from framework.logging import LoggingEntity
from settings.models import Settings


@dataclass
class FileHandler(LoggingEntity):
    """Handler that validates the uploaded files and stores them safely.

    The accepted extensions and MIME types can be given when the handler is
    created, and default to the plain text ones that the wordlists use.
    """

    _allowed_extensions: list[str] | None = None
    _mime_types: list[str] | None = None

    @cached_property
    def allowed_extensions(self) -> list[str]:
        """The accepted extensions, including the empty one for files without it."""
        return self._allowed_extensions if self._allowed_extensions is not None else ["txt", "text", ""]

    @cached_property
    def mime_types(self) -> list[str]:
        """The accepted MIME types, detected from the content of the file."""
        return self._mime_types if self._mime_types is not None else ["text/plain"]

    def _validate_size(self, in_memory_file: Any) -> None:
        """Check that the file isn't bigger than the configured maximum size.

        Args:
            in_memory_file: Uploaded file, whose size is read from its metadata.

        Raises:
            ValidationError: If the file is too large.
        """
        max_mb_size = Settings.objects.first().max_uploaded_file_mb
        size = in_memory_file.size / (1024 * 1024)
        if size > max_mb_size:
            self.logger.warning(f"[Security] Attempt of upload too large file with {size} MB")
            raise ValidationError(
                f"File size is greater than the max size allowed ({max_mb_size} MB)",
                code="file",
                params={"value": size},
            )

    def _validate_extension(self, in_memory_file: Any) -> None:
        """Check that the file has one of the accepted extensions.

        Args:
            in_memory_file: Uploaded file, whose extension is taken from the name
              that the user provided.

        Raises:
            ValidationError: If the extension isn't accepted.
        """
        extension = Path(in_memory_file.name).suffix[1:].lower()
        if extension not in self.allowed_extensions:
            self.logger.warning(f"[Security] Attempt of upload file with invalid extension: {extension}")
            raise ValidationError("Invalid extension", code="file", params={"value": extension})

    def _validate_mime_type(self, in_memory_file: Any) -> None:
        """Check the MIME type of the file content, and not the one it claims.

        Args:
            in_memory_file: Uploaded file, which is read from its current position,
              so this check runs before anything else consumes it.

        Raises:
            ValidationError: If the detected MIME type isn't accepted.
        """
        # The first 1024 bytes are enough for libmagic to identify the file type from its content
        mime_type = magic.from_buffer(in_memory_file.read(1024), mime=True)
        if mime_type not in self.mime_types:
            self.logger.warning(f"[Security] Attempt of upload file with invalid MIME type: {mime_type}")
            raise ValidationError("Invalid MIME type", code="file", params={"value": mime_type})

    def validate_file(self, in_memory_file: Any) -> None:
        """Check the size, the extension, and the MIME type of an uploaded file.

        Args:
            in_memory_file: Uploaded file to validate before storing it.

        Raises:
            ValidationError: If any of the three checks rejects the file.
        """
        self._validate_size(in_memory_file)
        self._validate_extension(in_memory_file)
        self._validate_mime_type(in_memory_file)

    def validate_filepath_checksum(self, filepath: str, expected_checksum: str) -> bool:
        """Check that a stored file still has the checksum it had when it was stored.

        Args:
            filepath: Path of the stored file.
            expected_checksum: SHA-512 checksum returned by store_file.

        Returns:
            Whether the content of the file is still the same one.
        """
        with open(filepath, "rb") as file:
            checksum = hashlib.sha512(file.read()).hexdigest()
            return checksum == expected_checksum

    def store_file(self, directory: Path, in_memory_file: Any) -> tuple[str, str, int]:
        """Store an uploaded file, naming it with a random UUID.

        The name provided by the user is discarded, so it can't be used to write
        outside the target directory or to overwrite another file.

        Args:
            directory: Directory where the file is written.
            in_memory_file: Uploaded file, already validated.

        Returns:
            The path where the file was stored, its SHA-512 checksum, and the number
            of lines it contains.
        """
        path = directory / f"{str(uuid.uuid4())}.txt"
        checksum = hashlib.sha512()
        with path.open("wb") as stored_file:
            for chunk in in_memory_file.chunks():
                stored_file.write(chunk)
                checksum.update(chunk)
        lines = 0
        with open(path, "rb") as stored_file:
            lines = len(stored_file.readlines())
        self.logger.warning(f"[Security] New file uploaded to the server in the path {path}")
        return str(path), checksum.hexdigest(), lines
