"""Base input class of version 1.x, kept only so its migrations can still be imported.

Deprecated. Nothing but the restored version 1.x migrations should reference this module,
and it must be removed once they are squashed away.
"""


class BaseInput:
    """Placeholder for the version 1.x base of the models used as tool input.

    The restored migrations only create tables, so they never instantiate their historical
    models and never reach any of the original methods. Only the name and the import path
    matter here.
    """
