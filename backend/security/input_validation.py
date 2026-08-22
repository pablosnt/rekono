"""Input validators of version 1.x, kept only so its migrations can still be imported.

Deprecated. Nothing but the restored version 1.x migrations should reference this module,
and it must be removed once they are squashed away.
"""


def validate_name(value: str) -> None:
    """Placeholder for the version 1.x validation of names."""


def validate_text(value: str) -> None:
    """Placeholder for the version 1.x validation of free text values."""


def validate_url(value: str) -> None:
    """Placeholder for the version 1.x validation of URLs."""


def validate_cve(value: str) -> None:
    """Placeholder for the version 1.x validation of CVE identifiers."""


def validate_credential(value: str) -> None:
    """Placeholder for the version 1.x validation of credentials."""


def validate_telegram_token(value: str) -> None:
    """Placeholder for the version 1.x validation of Telegram bot tokens."""


def validate_defect_dojo_api_key(value: str) -> None:
    """Placeholder for the version 1.x validation of Defect-Dojo API keys."""


def validate_number(value: int) -> None:
    """Placeholder for the version 1.x validation of numbers."""


def validate_time_amount(value: int) -> None:
    """Placeholder for the version 1.x validation of amounts of time."""


def validate_upload_file_size(value: int) -> None:
    """Placeholder for the version 1.x validation of the uploaded file sizes."""
