"""Target denylist management module for Rekono.

This module provides target denylist functionality for security testing operations.
It manages a centralized list of targets, expressed as exact values, regex patterns,
or IP networks, that must be excluded from security assessments.

Key Features:
    - TargetDenylist model storing target patterns as system-managed default
      entries or user-added custom entries
    - Blocked counter on each entry, incremented whenever it denies a target
    - Fixture-based provisioning of default entries, with custom entries
      preserved across data recreation
    - REST API endpoints for denylist CRUD operations with filtering and
      search on the target field

Architecture:
    Denylist entries are consulted by the target validator during target
    validation, before a target is accepted. Each candidate value, together
    with the addresses or hostname it resolves to over DNS, is checked for an
    exact match, a regex match, or IP network membership against every entry.
    Default entries are reloaded from fixtures on migration, while custom
    entries created through the REST API survive that reload.

Security:
    - Input validation restricting the characters allowed in target patterns
    - Role-based permissions restricting denylist creation and modification
      to administrators
    - Default entries are excluded from update and delete operations to
      protect system-wide exclusions from unauthorized changes
"""
