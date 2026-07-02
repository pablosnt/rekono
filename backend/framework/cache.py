"""Redis-backed cache for expensive, repeatable lookups.

Provides the Cache class, a small key-value wrapper around the Redis
connection already managed by RQ. Callers instantiate one Cache per purpose
(e.g. BaseInput.url_cache) rather than sharing a single global instance.
"""

from dataclasses import dataclass
from functools import cached_property

import django_rq
from redis import Redis


@dataclass
class Cache:
    """Redis-backed key-value cache with a configurable TTL and key prefix.

    Reuses the Redis connection already managed by RQ (see the "cache" entry
    in RQ_QUEUES) instead of provisioning a separate one. The connection is
    resolved lazily on first use and then reused for every subsequent call.

    Attributes:
        prefix (str): Namespace prepended to every key, to keep this cache's
                      entries distinguishable from other Cache instances that
                      may share the same Redis keyspace.
        ttl (int): Expiration time in seconds applied to every stored value.
        queue (str): RQ queue name used to resolve the shared Redis connection.
    """

    prefix: str
    ttl: int = 7200
    queue: str = "cache"

    @cached_property
    def connection(self) -> Redis:
        """Resolve and cache the Redis connection for this instance.

        Reuses RQ's connection handling instead of opening a dedicated one.
        Evaluated once per Cache instance since cached_property memoizes the
        result after the first access.

        Returns:
            Redis: Redis client backing the configured RQ queue.
        """
        return django_rq.get_connection(self.queue)

    def _key(self, key: str) -> str:
        """Build the namespaced Redis key for a given logical key.

        Args:
            key (str): Logical cache key supplied by the caller.

        Returns:
            str: Key prefixed with this cache's namespace.
        """
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> str | None:
        """Retrieve a cached value.

        Args:
            key (str): Logical cache key to look up.

        Returns:
            str | None: The cached value, decoded to a string, or None if
                        the key isn't cached or has expired.
        """
        value = self.connection.get(self._key(key))
        return None if value is None else value.decode()

    def set(self, key: str, value: str) -> None:
        """Store a value in the cache with this instance's TTL.

        Args:
            key (str): Logical cache key to store the value under.
            value (str): Value to cache.
        """
        self.connection.setex(self._key(key), self.ttl, value)
