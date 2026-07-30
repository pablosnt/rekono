"""VulnCheck NVD++ vulnerability intelligence platform integration for Rekono.

Provides integration with VulnCheck's NVD++ service, which mirrors the National
Vulnerability Database (NVD) schema and additionally supplies pre-resolved,
VulnCheck-specific CPE configuration details for affected technologies.
Authentication via a Bearer API token is required for all requests.

Key Features:
    - CVE data enrichment using VulnCheck's enhanced NVD++ index
    - Bearer token authentication for secure API access
    - Full reuse of NVD NIST parsing logic (identical response schema)
    - Availability gated on required API token presence
    - Quality scoring inherited from NvdNist (status-based penalties applied)
"""
