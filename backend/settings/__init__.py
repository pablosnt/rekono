"""Settings module for Rekono.

This module provides centralized configuration management for global system settings
within the Rekono security platform. It manages runtime application configuration,
network proxy settings, and security policy controls that affect the entire platform.

Key Features:
    - Global proxy configuration (all_proxy, http_proxy, https_proxy, ftp_proxy, no_proxy)
      with target format validation
    - Configurable maximum upload size for uploaded files, bounded to prevent
      resource exhaustion
    - Toggle to enable or disable automatic fixing of findings
    - REST API endpoint for reading and updating the platform settings

Architecture:
    Settings are managed as a singleton model instance, seeded through a fixture
    on first deployment and left untouched afterwards, with automatic validation
    and secure API exposure for administrative access.

Security:
    - Access is restricted to authenticated users holding the required Django
      model permissions for the Settings model
    - Proxy fields are validated against the target format regex before storage
    - The API only exposes GET and PUT, so the settings instance cannot be
      created or deleted through it
"""
