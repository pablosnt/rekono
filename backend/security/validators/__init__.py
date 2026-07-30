"""Security validators for input, targets and passwords across Rekono.

This module provides the validators attached to Django model fields, serializers
and the password validation framework to gate what values Rekono accepts, from
general user input to penetration testing targets. The regex patterns shared by
these validators are centralized in the Regex enum (enums.py) so every field
that needs the same shape of value (a name, a path, a CVE identifier, and so on)
validates it consistently.

Key Features:
    - Regex pattern library (Regex enum) covering names, free text, targets,
      paths, CVE identifiers, secrets, and known injection and sensitive
      environment variable patterns
    - Generic regex-based value validation (Validator) with optional detection
      of injection characters and sensitive environment variable assignments,
      the latter used to stop a value from hijacking a tool subprocess when it
      is rendered into an executed command
    - Future-datetime validation (FutureDatetimeValidator) for fields such as
      expiration dates
    - Password complexity validation (PasswordValidator) enforcing minimum
      length and character diversity, plugged into Django's password
      validation framework
    - Penetration testing target validation (TargetValidator) that layers deny
      list enforcement (exact match, regex, and IP network) on top of regex
      format checks, and resolves each target's DNS-forward or reverse address
      so a denied target can't be reached indirectly through name resolution

Security:
    - All validation failures are logged as security events
    - Deny list matching tolerates malformed entries (invalid regex or network)
      so one bad entry can't crash validation or let a target slip through
    - Targets are normalized (lower-cased, trailing dot stripped) before deny
      list matching so case or FQDN variants can't bypass a denied entry
"""
