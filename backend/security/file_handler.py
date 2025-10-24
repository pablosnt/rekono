"""Secure file handling utilities for Rekono.

Provides secure file upload validation, storage, and integrity verification
for user-uploaded content. This module implements defense-in-depth security
controls to prevent malicious file uploads and ensure data integrity throughout
the file lifecycle.
"""

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
    """Secure file handling class providing upload validation and storage capabilities.

    Implements comprehensive file security controls including multi-layer validation,
    secure storage with integrity verification, and defensive measures against
    common file upload attack vectors. This class serves as the central file
    security service for the Rekono platform.

    Security Architecture:
        - Defense-in-depth validation with size, extension, and MIME type checks
        - Content-based MIME type detection to prevent extension spoofing
        - Cryptographic integrity verification using SHA-512 checksums
        - Secure file naming to prevent path traversal attacks
        - Comprehensive audit logging for security monitoring

    Attributes:
        _allowed_extensions (list[str]): Whitelist of permitted file extensions (default: txt, text, empty).
        _mime_types (list[str]): Whitelist of permitted MIME types (default: text/plain).

    Example:
        Validate and store a user-uploaded file:

        ```python
        handler = FileHandler()
        handler.validate_file(uploaded_file)
        path, checksum, lines = handler.store_file(storage_dir, uploaded_file)
        ```
    """

    _allowed_extensions: list[str] | None = None
    _mime_types: list[str] | None = None

    @cached_property
    def allowed_extensions(self) -> list[str]:
        """Get the whitelist of permitted file extensions for upload validation.

        Returns the configured allowed extensions or default whitelist if not set.
        Used for extension-based validation to prevent upload of dangerous file types.

        Returns:
            list[str]: List of allowed file extensions including txt, text, and empty string.
        """
        return self._allowed_extensions if self._allowed_extensions is not None else ["txt", "text", ""]

    @cached_property
    def mime_types(self) -> list[str]:
        """Get the whitelist of permitted MIME types for content validation.

        Returns the configured allowed MIME types or default whitelist if not set.
        Used for content-based validation to prevent MIME type spoofing attacks.

        Returns:
            list[str]: List of allowed MIME types with text/plain as default.
        """
        return self._mime_types if self._mime_types is not None else ["text/plain"]

    def _validate_size(self, in_memory_file: Any) -> None:
        """Validate uploaded file size against configured limits.

        Checks the uploaded file size against the system-configured maximum
        file size limit to prevent DoS attacks via oversized uploads.
        Logs security warnings for rejected uploads.

        Args:
            in_memory_file (Any): Django InMemoryUploadedFile object to validate.

        Raises:
            ValidationError: If file size exceeds the configured maximum limit.
        """
        max_mb_size = Settings.objects.first().max_uploaded_file_mb
        size = in_memory_file.size / (1024 * 1024)  # Get file size in MB
        if size > max_mb_size:  # File size greater than size limit
            self.logger.warning(f"[Security] Attempt of upload too large file with {size} MB")
            raise ValidationError(
                f"File size is greater than the max size allowed ({max_mb_size} MB)",
                code="file",
                params={"value": size},
            )

    def _validate_extension(self, in_memory_file: Any) -> None:
        """Validate uploaded file extension against whitelist.

        Checks the uploaded file's extension against the configured whitelist
        of allowed extensions. This prevents upload of potentially dangerous
        file types while logging security events for rejected uploads.

        Args:
            in_memory_file (Any): Django InMemoryUploadedFile object to validate.

        Raises:
            ValidationError: If file extension is not in the allowed extensions list.
        """
        extension = Path(in_memory_file.name).suffix[1:].lower()  # Get file extension
        if extension not in self.allowed_extensions:
            self.logger.warning(f"[Security] Attempt of upload file with invalid extension: {extension}")
            raise ValidationError("Invalid extension", code="file", params={"value": extension})

    def _validate_mime_type(self, in_memory_file: Any) -> None:
        """Validate uploaded file MIME type using content analysis.

        Performs content-based MIME type detection using libmagic to prevent
        extension spoofing attacks. Validates detected MIME type against
        the configured whitelist and logs security events for violations.

        Args:
            in_memory_file (Any): Django InMemoryUploadedFile object to validate.

        Raises:
            ValidationError: If detected MIME type is not in the allowed types list.
        """
        mime_type = magic.from_buffer(in_memory_file.read(1024), mime=True)
        if mime_type not in self.mime_types:
            self.logger.warning(f"[Security] Attempt of upload file with invalid MIME type: {mime_type}")
            raise ValidationError("Invalid MIME type", code="file", params={"value": mime_type})

    def validate_file(self, in_memory_file: Any) -> None:
        """Perform comprehensive validation of uploaded file.

        Executes multi-layer validation including file size, extension,
        and MIME type checks to ensure uploaded files meet security
        requirements. All validation failures are logged for security monitoring.

        Args:
            in_memory_file (Any): Django InMemoryUploadedFile object to validate.

        Raises:
            ValidationError: If any validation check fails (size, extension, or MIME type).
        """
        self._validate_size(in_memory_file)
        self._validate_extension(in_memory_file)
        self._validate_mime_type(in_memory_file)

    def validate_filepath_checksum(self, filepath: str, expected_checksum: str) -> bool:
        """Validate file integrity using SHA-512 checksum verification.

        Computes and verifies the SHA-512 checksum of a stored file against
        an expected value to detect tampering or corruption. This provides
        cryptographic integrity verification for stored files.

        Args:
            filepath (str): Path to the file to verify.
            expected_checksum (str): Expected SHA-512 hexadecimal checksum.

        Returns:
            bool: True if checksums match, False if integrity check fails.
        """
        with open(filepath, "rb+") as file:
            checksum = hashlib.sha512(file.read()).hexdigest()
            return checksum == expected_checksum

    def store_file(self, directory: Path, in_memory_file: Any) -> tuple[str, str, int]:
        """Securely store uploaded file with integrity verification.

        Stores the validated file in the specified directory using a UUID-based
        filename to prevent path traversal attacks. Computes SHA-512 checksum
        during storage for integrity verification and counts file lines for
        metadata tracking. Logs the storage event for security audit.

        Args:
            directory (Path): Target directory for file storage.
            in_memory_file (Any): Django InMemoryUploadedFile object to store.

        Returns:
            tuple[str, str, int]: File path, SHA-512 checksum, and line count.
        """
        path = directory / f"{str(uuid.uuid4())}.txt"
        checksum = hashlib.sha512()
        with path.open("wb+") as stored_file:
            for chunk in in_memory_file.chunks():
                stored_file.write(chunk)
                checksum.update(chunk)
        lines = 0
        with open(path, "rb+") as stored_file:
            lines = len(stored_file.readlines())
        self.logger.warning(f"[Security] New file uploaded to the server in the path {path}")
        return str(path), str(checksum), lines
