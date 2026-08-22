"""Background job that keeps the vulnerability data up to date.

The monitor asks the threat intelligence platforms which CVEs are trending and what
their exploitation probability is, so the findings that Rekono already discovered
reflect how dangerous they are today. It also recovers the executions whose job
disappeared, since nothing else would move them out of their status.
"""
