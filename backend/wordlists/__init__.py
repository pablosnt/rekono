"""Wordlist management module for Rekono.

This module provides comprehensive wordlist management for security testing and
reconnaissance activities. It handles file-based wordlists used by security tools
for enumeration, directory brute-forcing, subdomain discovery, and other automated
testing scenarios requiring large input datasets.

Security:
    - Secure file handling with validation and checksum verification
    - User-scoped access control and ownership management
    - Safe file storage with proper permissions and validation
    - Input sanitization and injection prevention for wordlist metadata
"""
