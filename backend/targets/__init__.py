"""Target management module for Rekono.

This module provides comprehensive target management functionality for security testing
workflows. It handles the identification, validation, and classification of various
target types including IP addresses, networks, domains, and IP ranges for automated
security assessment operations.

Target Type Support:
    - Private IP: RFC 1918 private IPv4 and IPv6 addresses
    - Public IP: Internet-routable IPv4 and IPv6 addresses
    - Network: CIDR notation networks (e.g., 192.168.1.0/24)
    - IP Range: Hyphen-separated IP ranges (e.g., 192.168.1.1-192.168.1.100)
    - Domain: DNS-resolvable domain names and hostnames

Security:
    - Project-level access control and permission enforcement
    - Input validation and sanitization for target specifications
    - Integration with security testing frameworks and tools
    - Target classification that distinguishes private from public IP scope
"""
