"""Validation of the values that Rekono accepts.

The regex patterns are centralized in the Regex enum, so every field that holds the
same kind of value validates it the same way. Besides the generic validation, this
package implements the password complexity policy and the target validation, which
enforces the deny list that keeps the scans away from the forbidden hosts.
"""
