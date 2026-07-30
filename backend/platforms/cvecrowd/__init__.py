"""CVE Crowd integration platform for Rekono.

This module provides comprehensive integration with the CVE Crowd threat intelligence
platform for real-time vulnerability trending analysis and alerting. The integration
enables security teams to identify and prioritize trending vulnerabilities through
automated monitoring, intelligent alerting, and seamless API connectivity with the
CVE Crowd service for enhanced threat detection capabilities.

Key Features:
    - Real-time trending CVE detection and vulnerability prioritization
    - Automated vulnerability monitoring with configurable time spans
    - Integration with Rekono's alerting system for trending vulnerability notifications
    - Secure API token management with encrypted credential storage
    - Background monitoring jobs with intelligent vulnerability correlation
    - REST API endpoints for CVE Crowd platform configuration and management

Integration Architecture:
    The CVE Crowd integration follows Rekono's platform architecture pattern with
    settings management, secure API connectivity, and finding processing capabilities.
    The system automatically correlates discovered vulnerabilities with trending CVE
    data to provide prioritized security intelligence and actionable threat insights.

Security:
    - Encrypted API token storage using AES encryption
    - Secure API communication with bearer token authentication
    - Input validation for configuration parameters via model field validators
    - Access restricted to authenticated users holding the required Django
      model permissions (RekonoModelPermission)
"""
