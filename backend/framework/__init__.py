"""Base classes and shared infrastructure used by all the Rekono apps.

Provides the base models that implement the project scoping and the tool input
system, the base viewsets, serializers, and filters that keep the API consistent,
and the cross-cutting pieces that the apps rely on: the request context, the
logging filter, the job queues, the Redis cache, and the integration platforms.
"""
