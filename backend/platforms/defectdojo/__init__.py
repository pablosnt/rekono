"""DefectDojo integration platform for Rekono.

This module provides comprehensive integration with OWASP DefectDojo vulnerability
management platform, enabling automated security finding synchronization and
centralized vulnerability tracking for security teams. The integration supports
bidirectional data flow between Rekono's security testing platform and DefectDojo's
vulnerability management capabilities for streamlined security operations.

Key Features:
    - Automated vulnerability finding synchronization to DefectDojo
    - Project-level integration with product and engagement management
    - Target-specific engagement isolation for granular vulnerability tracking
    - Support for both scan file imports and manual finding creation
    - Real-time availability checking and connection validation
    - Hierarchical data organization (Product Types - Products - Engagements - Tests)

Integration Workflow:
    - DefectDojo settings configuration with secure API token management
    - Project synchronization mapping to DefectDojo products and engagements
    - Automated finding export after security tool execution completion
    - Support for both native scan file imports and generic finding data
    - Endpoint creation for web application security testing results
    - Tag-based organization and filtering for vulnerability management

Data Synchronization:
    - Security findings mapped to DefectDojo finding format with severity conversion
    - Web endpoints synchronized for application security testing results
    - Execution results linked to DefectDojo tests for audit trail maintenance
    - Project-level and target-level engagement management for organizational clarity

Security:
    - Encrypted API token storage with AES encryption
    - TLS certificate validation for secure API communications
    - Project-level access control and permission enforcement
    - Input validation and injection prevention for all DefectDojo API interactions
"""
