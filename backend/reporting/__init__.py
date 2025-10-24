"""Security reporting and document generation module for Rekono.

This module provides comprehensive security reporting capabilities for generating
detailed assessments and exporting security findings in various formats. The system
supports multi-format report generation including PDF, JSON, and XML outputs with
customizable content filtering and automated delivery through multiple channels.

Report Types:
    - PDF Reports: Executive-ready documents with visual statistics and detailed findings
    - JSON Reports: Machine-readable exports for integration with external tools
    - XML Reports: Structured data exports compatible with vulnerability scanners

Architecture:
    The reporting system uses a multi-threaded approach where report generation occurs
    in background threads to prevent API blocking. Reports are generated from filtered
    findings data with support for complex query criteria including project membership,
    triage status, and finding type selections.

Security:
    - Project-level access control ensuring users only access authorized report data
    - Secure file storage in dedicated directories with unique filename generation
    - Input validation and sanitization for all report parameters and filtering criteria
    - Audit logging for report generation activities and access patterns
    - Integration with external notification platforms using secure authentication
"""
