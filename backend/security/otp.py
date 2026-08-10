from datetime import datetime


def get_expiration() -> datetime | None:
    """Get the expiration of a one-time password.

    Returns:
        Always None. Django applies the defaults of the fields in Python instead
        of writing them to the schema, and the restored migrations only create
        tables, so this default is never applied.
    """
    return None
