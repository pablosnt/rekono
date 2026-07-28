"""Input types module for Rekono.

This module manages the catalog of input type definitions used throughout the
Rekono security testing platform. Each input type (OSINT, Host, Port, Path,
Technology, Credential, Vulnerability, Exploit, Wordlist, Authentication,
Http Header) is mapped to the Django model that stores its data, letting tools,
executions, and findings resolve input data dynamically and discover
relationships between the input models used across the platform.

Key Features:
    - Input type catalog seeded from fixtures, with one InputType record per
      supported input category
    - Dynamic resolution of primary and fallback model references from
      'app.Model' string identifiers into the actual Django model classes
    - Relationship discovery between input types based on ForeignKey and
      reverse ForeignKey fields on their models, used for tool chaining and
      dependency ordering
    - Serializer exposing the input type name and model references in a
      JSON-friendly format

Architecture:
    The input types system uses a mapping-based approach where each input type
    is associated with a primary Django model and an optional fallback model
    used when the primary one is unavailable. Relationship calculation walks
    the primary model's fields to find other input types it depends on
    (parents) or that depend on it (children), enabling tool workflows to be
    ordered and chained correctly.

Security:
    - Input type records are managed only through the Django admin site,
      gated by the standard Django model permissions; there is no REST API
      surface for creating, updating, or deleting them
"""
