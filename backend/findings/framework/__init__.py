"""Base classes that all the kinds of findings are built on.

Implement what every finding has in common: the deduplication across executions,
the fixing and unfixing when a finding stops being detected, the triage of the ones
that can be reviewed, and the API that exposes all of them the same way.
"""
