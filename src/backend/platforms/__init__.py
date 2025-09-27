"""Platform integrations module for Rekono.

This module provides the foundation for external platform integrations that enhance
security findings with additional intelligence, documentation, and metadata. Platform
integrations automatically process discovered findings to enrich them with valuable
context from external security resources and threat intelligence sources.

Key Features:
    - Automated finding enrichment with external platform data
    - HackTricks integration for penetration testing methodologies and guides
    - Host metadata enrichment with geolocation and DNS resolution
    - NVD NIST vulnerability intelligence integration for CVE enrichment
    - Extensible integration framework for custom platform connectors
    - Asynchronous processing for scalable intelligence gathering

Integration Architecture:
    - BaseIntegration provides common functionality for all platform connectors
    - Finding-specific processors enrich data based on discovery type
    - Automatic integration triggering based on finding characteristics
    - Configurable integration settings and authentication management
    - Error handling and retry mechanisms for reliable data collection

Security:
    - Secure API credential management with encryption
    - Rate limiting and request throttling for external API compliance
    - Input validation and sanitization for all external data
    - Audit logging for all platform integration activities
    - Network timeout and security controls for external connections
"""
