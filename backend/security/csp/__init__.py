"""Content Security Policy violation reporting for the Rekono security module.

Provides browser-facing endpoints that receive and log CSP violation reports
delivered by the browser's built-in reporting mechanism. Supports both the modern
Reporting API ``report-to`` format and the legacy ``report-uri`` delivery format
so that all browsers can contribute to violation monitoring regardless of their
Reporting API support level.
"""
