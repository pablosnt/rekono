"""Redis-backed cache for expensive, repeatable lookups.

Provides the Cache class, a small key-value wrapper around the Redis
connection already managed by RQ. Callers instantiate one Cache per purpose
(e.g. BaseInput._url_cache) rather than sharing a single global instance.
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
        prefix: Namespace prepended to every key, to keep this cache's entries
          distinguishable from other Cache instances that may share the same Redis
          keyspace.
        ttl: Expiration time in seconds applied to every stored value.
        queue: RQ queue name used to resolve the shared Redis connection.
    """

    prefix: str
    ttl: int = 7200
    queue: str = "cache"

    @cached_property
    def connection(self) -> Redis:
        """The Redis client backing the configured RQ queue, resolved on first use."""
        return django_rq.get_connection(self.queue)

    def _key(self, key: str) -> str:
        """Build the namespaced Redis key for a given logical key.

        Args:
            key: Logical key, without the prefix of this cache instance.

        Returns:
            The key as it is actually stored in Redis.
        """
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> str | None:
        """Get a cached value.

        Args:
            key: Logical key, without the prefix of this cache instance.

        Returns:
            The cached value decoded to a string, or None if the key isn't cached
            or has expired.
        """
        value = self.connection.get(self._key(key))
        return value.decode() if isinstance(value, bytes) else value

    def set(self, key: str, value: str) -> None:
        """Store a value in the cache with this instance's TTL.

        Args:
            key: Logical key, without the prefix of this cache instance.
            value: Value to store, overwriting any previous one and resetting its
              expiration.
        """
        self.connection.setex(self._key(key), self.ttl, value)
