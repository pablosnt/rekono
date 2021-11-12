import hashlib
from pathlib import Path
from typing import Any

import magic
from django.core.exceptions import ValidationError

from rekono.settings import FILE_UPLOAD_MAX_SIZE


def validate(in_memory_file: Any, extensions: list, mime_types: list) -> None:
    size = in_memory_file.size / (1024 * 1024)
    if size > FILE_UPLOAD_MAX_SIZE:
        raise ValidationError(
            {'file': f'File size is greater than the max size allowed ({FILE_UPLOAD_MAX_SIZE} MB)'}
        )
    extension = Path(in_memory_file.name).suffix[1:].lower()
    if extension not in extensions:
        raise ValidationError({'file': f'Invalid extension {extension}'})
    mime_type = magic.from_buffer(in_memory_file.read(1024), mime=True)
    if mime_type not in mime_types:
        raise ValidationError({'file': f'Invalid MIME type {mime_type}'})


def check_checksum(filepath: str, expected: str) -> bool:
    with open(filepath, 'rb+') as file:
        value = hashlib.sha512(file.read()).hexdigest()
        return value == expected


def store_file(in_memory_file: Any, filename: str) -> str:
    checksum = hashlib.sha512()
    with open(filename, 'wb+') as storage:
        for chunk in in_memory_file.chunks():
            storage.write(chunk)
            checksum.update(chunk)
    return checksum.hexdigest()
