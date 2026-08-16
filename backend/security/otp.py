"""One-time password helper of version 1.x, kept only so its migrations can still be imported.

Deprecated. Nothing but the restored version 1.x migrations should reference this module,
and it must be removed once they are squashed away.
"""

from datetime import datetime


def get_expiration() -> datetime | None:
    """Get the expiration of a one-time password.

    Returns:
        Always None. Django applies the defaults of the fields in Python instead of writing
        them to the schema, and the restored migrations only create tables, so this default
        is never applied.
    """
    return None
