"""External platforms that Rekono works with.

The platforms are grouped by what they do: the CVE providers complete the
vulnerabilities with the data of their advisories, the integrations add whatever
they know about a finding, and the notifications tell the users about them. The
platforms that need to be configured have their own app with their settings, and
the ones that only need a public API are a single module.
"""
