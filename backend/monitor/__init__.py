"""Monitor module for Rekono.

This module provides automated background monitoring of external threat
intelligence sources, keeping Rekono's vulnerability data current without
manual intervention. It schedules and executes recurring jobs that refresh
trending CVE data and EPSS scores.

Key Features:
    - Configurable monitoring interval via MonitorSettings (24-168 hours)
    - Self-scheduling RQ jobs that reschedule themselves on completion
    - Integration with external threat intelligence platforms (CveCrowd, First/EPSS)
    - REST API endpoint for viewing and updating monitoring configuration
    - Management command for manually triggering a monitoring run
"""
