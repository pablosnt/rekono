"""DefectDojo integration platform for Rekono.

This module provides an outbound integration with the OWASP DefectDojo vulnerability
management platform. Rekono pushes security findings to DefectDojo after each tool
execution completes, it never reads findings back from DefectDojo. A Rekono project
maps to a DefectDojo product and engagement, and an individual target can be pinned to
its own engagement for finer-grained tracking within that same product.

Key Features:
    - Automated vulnerability finding synchronization to DefectDojo after each execution
    - Project-level mapping to a DefectDojo product and engagement
    - Optional per-target engagement override for granular vulnerability tracking
    - Native scan file imports for tools with a registered DefectDojo scan type, or a
      generic JSON finding import otherwise
    - Optional reimport into an existing test instead of creating a new one every time
    - Availability checking based on the configured server URL and API token

Integration Workflow:
    - DefectDojo settings store the server URL and API token used for every request
    - A project links to a DefectDojo product and, optionally, an engagement through
      DefectDojoSync
    - A target can override its parent project's engagement through DefectDojoTargetSync
    - When neither the target nor the project has an engagement configured yet, one is
      created automatically and remembered as a new target sync
    - After execution, tool-detected findings (excluding Path findings and any finding
      entered manually by a user) are imported or reimported as a DefectDojo test
    - If no target sync or project sync exists for the execution's target, or the tool's
      native report file is missing, the findings are left unsynchronized without error

Security:
    - Encrypted API token storage with AES encryption
    - TLS certificate validation for secure API communications
    - Project-level access control and permission enforcement
"""
