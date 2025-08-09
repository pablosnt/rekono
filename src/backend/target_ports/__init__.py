"""Target ports management module for Rekono.

This module provides comprehensive management of target ports within security testing
workflows. It handles the association between targets and specific ports, enabling
precise service enumeration, authentication management, and security testing execution
on network services and web applications.

Target Port Architecture:
    Target ports serve as the fundamental unit for security testing operations,
    linking targets with specific services running on designated ports. Each
    target port can optionally include path information for web-based services
    and authentication credentials for authenticated testing scenarios.

Security:
    - Project-level access control through target association
    - Input validation and sanitization for port numbers and paths
    - Secure handling of authentication credentials per port
    - Integration with security testing frameworks and tools
"""
