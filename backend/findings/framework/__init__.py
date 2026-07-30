"""Framework components for findings management in Rekono.

This submodule provides the foundational framework components for the findings
system, including base model classes, filters, serializers, and views that all
specific finding types build on. The framework provides common functionality
such as deduplication, fixing/unfixing, and DefectDojo integration, while
enabling specialization for finding types that require a triage workflow.
"""
