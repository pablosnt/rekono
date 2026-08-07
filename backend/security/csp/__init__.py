"""Reporting of the Content Security Policy violations.

Provides the endpoints where the browsers deliver the CSP violation reports, both in
the modern Reporting API format and in the legacy one, and logs them for later
review. The policy itself is defined and enforced by the security middleware.
"""
