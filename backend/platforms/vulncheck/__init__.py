"""VulnCheck NVD++ vulnerability intelligence platform integration for Rekono.

Provides integration with VulnCheck's NVD++ service, which mirrors the National
Vulnerability Database (NVD) schema and enriches it with additional threat
intelligence including CISA Known Exploited Vulnerabilities (KEV) data and
VulnCheck-specific CPE configuration details. Authentication via a Bearer
API token is required for all requests.

Key Features:
    - CVE data enrichment using VulnCheck's enhanced NVD++ index
    - Bearer token authentication for secure API access
    - Full reuse of NVD NIST parsing logic (identical response schema)
    - Availability gated on required API token presence
    - Quality scoring inherited from NvdNist (status-based penalties applied)
"""
