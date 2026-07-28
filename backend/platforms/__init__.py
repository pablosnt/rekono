"""Platform integrations module for Rekono.

This module provides the foundation for external platform integrations that enhance
security findings with additional intelligence, documentation, and metadata. Platform
integrations automatically process discovered findings to enrich them with valuable
context from external security resources and threat intelligence sources.

Key Features:
    - Automated finding enrichment with external platform data
    - HackTricks integration for penetration testing methodologies and guides
    - Host metadata enrichment with DNS reverse resolution and geolocation
    - CVE enrichment from multiple providers (NVD NIST, VulnCheck, OSV, EUVD and GHSA),
      each scored for data quality so the best match wins when more than one provider
      returns data for the same CVE
    - EPSS exploitation probability from FIRST, applied directly to the finding rather
      than competing with the CVE providers
    - VirusTotal integration for host reputation, detection vote counts, and WHOIS data
    - CVE Crowd trending vulnerability monitoring and alerting
    - DefectDojo vulnerability management synchronization
    - SMTP and Telegram notification platform support
    - Extensible base classes (BaseIntegration, BaseCveProvider, BaseNotification) for
      adding new platform connectors

Integration Architecture:
    - BaseIntegration provides common functionality for all platform connectors
    - Finding-specific processors enrich data based on discovery type
    - Automatic integration triggering based on finding characteristics
    - Configurable integration settings and authentication management
    - Integrations run inside Rekono's asynchronous findings queue, so a slow or
      failing platform never blocks the others

Reliability and Security:
    - Secure API credential management through encrypted settings models
    - Automatic retries with backoff for transient HTTP errors and connection failures
    - Every external request is logged, and processing errors are caught and logged
      per finding so one failure doesn't stop the rest of the batch
"""
