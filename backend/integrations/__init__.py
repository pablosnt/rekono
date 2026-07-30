"""Third-party integrations module for Rekono.

This module manages the catalog of third-party platforms that Rekono can draw on
to enrich its security testing data, such as CVE databases, vulnerability
management platforms, and other security intelligence services. Each integration
is a simple registry record combining display metadata (name, description,
reference and icon URLs) with an enabled flag; the credentials and connection
details needed to actually use a platform are configured separately by that
platform's own settings module.

Key Features:
    - Centralized registry of available integrations with an enable/disable flag
    - REST API endpoints for listing integrations and toggling their enabled status
    - Full CRUD management of integration records through the Django admin interface
    - Fixture-based seeding that preserves user-configured enabled state, in both
      directions, across deployments and migrations
    - Icon and reference URL metadata for integration documentation and UI display

Security:
    - Django model permission enforcement: every role can view integrations, but
      only the Admin role can change their enabled status
    - The REST API exposes only the enabled field for updates, all other fields
      are read-only
"""
