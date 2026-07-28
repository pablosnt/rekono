"""Wordlist management module for Rekono.

This module provides comprehensive wordlist management for security testing and
reconnaissance activities. It handles file-based wordlists used by security tools
for enumeration, directory brute-forcing, subdomain discovery, and other automated
testing scenarios requiring large input datasets.

Key Features:
    - Secure wordlist file upload with validation and checksum-based integrity verification
    - Automatic size calculation by counting file lines after migrations and fixture loading
    - Wordlist type classification (Endpoint, Subdomain) for tool compatibility matching
    - User ownership with support for shared, ownerless default wordlists
    - Like functionality for community-driven wordlist curation
    - REST API endpoints for wordlist CRUD, filtering, searching, and ordering

Security:
    - Secure file handling with validation and checksum verification
    - User-scoped access control and ownership management
    - Safe file storage with UUID-based naming and validation
    - Input sanitization and injection prevention for wordlist metadata
"""
