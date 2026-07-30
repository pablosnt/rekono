"""HTTP headers management module for Rekono.

This module manages custom HTTP headers used during security testing operations.
It lets users configure header key/value pairs at three scopes: global headers
applied to every operation, user-specific headers tied to an individual account,
and target-specific headers tied to a single target, so that requests sent by
security tools carry the right authentication and customization data.

Key Features:
    - Multi-scope header configuration (global, user-specific, target-specific)
    - Input validation and injection prevention for header keys and values
    - Automatic inclusion of configured headers in tool execution commands via
      the Rekono execution framework
    - REST API endpoints for header management with project-based filtering
      and text search
    - Database constraints ensuring header uniqueness within each scope

Security:
    - Input validation and injection prevention for header keys and values
    - Project-level access control restricting target-specific headers to
      project members
    - Ownership checks ensuring users can only manage their own
      user-specific headers
    - Admin-only access for creating and updating global headers
"""
