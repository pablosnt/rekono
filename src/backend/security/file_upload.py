import hashlib
import logging
from pathlib import Path
from typing import Any, List

import magic
from django.core.exceptions import ValidationError
from system.models import System

logger = logging.getLogger()                                                    # Rekono logger


def validate(in_memory_file: Any, extensions: List[str], mime_types: List[str]) -> None:
    '''Validate in memory file based on size, extension and MIME type.

    Args:
        in_memory_file (Any): In memory file to validate
        extensions (List[str]): Allowed extensions
        mime_types (List[str]): Allowed MIME types

    Raises:
        ValidationError: Raised if file size, extension or MIME type is invalid
    '''
    max_size = System.objects.first().upload_files_max_mb                       # Max allowed file size
    size = in_memory_file.size / (1024 * 1024)                                  # Get file size in MB
    if size > max_size:                                                         # File size greater than size limit
        logger.warning(f'[Security] Attempt of upload too large file with {size} MB')
        raise ValidationError({'file': f'File size is greater than the max size allowed ({max_size} MB)'})
    extension = Path(in_memory_file.name).suffix[1:].lower()                    # Get file extension
    if extension not in extensions:                                             # Invalid file extension
        logger.warning(f'[Security] Attempt of upload file with invalid {extension} extension')
        raise ValidationError({'file': f'Invalid extension {extension}'})
    mime_type = magic.from_buffer(in_memory_file.read(1024), mime=True)         # Get MIME type from file content
    if mime_type not in mime_types:                                             # Invalid file MIME type
        logger.warning(f'[Security] Attempt of upload file with invalid {mime_type} MIME type')
        raise ValidationError({'file': f'Invalid MIME type {mime_type}'})


def check_checksum(filepath: str, expected: str) -> bool:
    '''Check if file checksum is equals to expected checksum or not.

    Args:
        filepath (str): File to check
        expected (str): Expected checksum

    Returns:
        bool: Indicate if file checksum matches the expected checksum
    '''
    with open(filepath, 'rb+') as file:
        value = hashlib.sha512(file.read()).hexdigest()                         # Calculate file hash using SHA-512
        return value == expected


def store_file(in_memory_file: Any, filepath: str) -> str:
    '''Store in memory file in a specific filepath.

    Args:
        in_memory_file (Any): In memory file to store
        filepath (str): Filepath where the in memory file will be stored

    Returns:
        str: Checksum of the stored file using SHA-512 algorithm
    '''
    checksum = hashlib.sha512()
    with open(filepath, 'wb+') as storage:                                      # Open filepath in write mode
        for chunk in in_memory_file.chunks():
            storage.write(chunk)                                                # Write file content
            checksum.update(chunk)                                              # Calculate hash value
    logger.warning(f'[Security] New file uploaded to the server in the path {filepath}')
    return checksum.hexdigest()
