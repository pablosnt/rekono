"""VirusTotal platform integration for host reputation and threat intelligence.

Provides the VirusTotal integration for Rekono, enriching Host findings on public IP
addresses or domains with reputation scores, analysis engine detection counts, and
WHOIS data retrieved from the VirusTotal API.

Key Features:
    - Reputation score and analysis engine detection counts (malicious, suspicious, total)
    - WHOIS data enrichment for domain investigation
    - Processing restricted to hosts on a public IP, so private network data is never
      sent to VirusTotal
    - Availability gated on the configured API key and cached in the database
"""
