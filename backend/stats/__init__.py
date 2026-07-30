"""Statistics and analytics module for Rekono.

This module provides read-only statistics endpoints covering security findings,
hosts, network services, technologies, and background job queues. Each endpoint
aggregates data with Django ORM annotations and exposes it through a REST API
for dashboards and reporting.

Key Features:
    - Aggregate counts of hosts, ports, and technologies grouped by common
      attributes such as OS type, service, or name
    - Vulnerability statistics grouped by CVE, CWE, severity, fix status, and
      exploit availability
    - Per-host vulnerability breakdowns combining total and severity-level counts
    - Triage status statistics combined across OSINT, credential, vulnerability,
      and exploit findings
    - Monthly evolution statistics tracking discovered, fixed, and active
      finding counts over time for each finding type
    - Redis Queue (RQ) statistics for monitoring background job health

Architecture:
    StatsViewSet is the shared base class for the queryset-based statistics
    endpoints (host, port, technology, vulnerability, triaging, and
    evolution), restricting access to authenticated users and GET requests
    only. MonthlyEvolutionViewSet specializes this base to compute per-month
    evolution statistics from any finding model referenced by a filterset,
    while TriagingStatsViewSet aggregates triage counts across multiple
    finding models in Python, since a single queryset union grouped by
    triage status isn't possible. RQ queue statistics are served separately
    by a plain APIView, outside this ViewSet hierarchy.

Security:
    - Project-level access control: statistics only include data from
      projects the requesting user is a member of
    - RQ queue statistics are restricted to Admin users, since they expose
      system-wide operational information rather than project-scoped data
"""
