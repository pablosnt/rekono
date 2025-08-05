"""Security findings management module for Rekono.

This module provides comprehensive management of security findings discovered
during security assessments. It handles the complete lifecycle of findings
from discovery to triage, including data models, filtering, serialization,
and REST API endpoints for various types of security-related information.

Key Features:
    - Comprehensive finding models covering hosts, ports, paths, vulnerabilities
    - Hierarchical finding relationships for detailed security analysis
    - Triage workflow for managing false positives and confirmed findings
    - Advanced filtering and search capabilities through REST API endpoints
    - Integration with DefectDojo for vulnerability management
    - Background processing for finding analysis and correlation

Finding Types:
    - OSINT: Open source intelligence data (IPs, domains, emails, etc.)
    - Host: Network hosts with geolocation and OS fingerprinting
    - Port: Network services with protocol and status information
    - Path: Web paths, API endpoints, and file shares
    - Technology: Software fingerprinting and version detection
    - Credential: Exposed authentication credentials and secrets
    - Vulnerability: Security vulnerabilities with CVE/CWE mapping
    - Exploit: Available exploits and proof-of-concept references

Security:
    - Project-level access control and permission enforcement
    - Secure handling of sensitive credential information
    - Input validation and sanitization for all finding data
    - Audit trails for finding lifecycle and triage decisions
"""
