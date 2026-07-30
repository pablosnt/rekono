"""Content Security Policy violation reporting for the Rekono security framework.

Provides browser-facing endpoints that receive and log Content Security Policy
violation reports delivered by the browser's built-in reporting mechanism. Supports
both the modern Reporting API ``report-to`` format and the legacy ``report-uri``
delivery format, so that all browsers can contribute to violation monitoring
regardless of their Reporting API support level. The module only records reports
for later review, it does not define, generate, or enforce the CSP itself.

Key Features:
    - Unauthenticated endpoints for the ``report-to`` and ``report-uri`` CSP delivery formats
    - Normalization of both single-object and array report payloads into individual violation records
    - Structured warning-level logging of each violation's blocked URI, origin, and triggering directive
    - Sanitization of attacker-controlled report fields, stripping control characters and capping length before logging
    - Always responds with HTTP 204, even for malformed payloads, so browsers keep sending reports

Security:
    - No authentication or permission checks, since browsers cannot attach credentials when delivering reports
    - Sanitized logging of blocked URI, origin, and directive values prevents log injection via control characters in violation payloads
"""
