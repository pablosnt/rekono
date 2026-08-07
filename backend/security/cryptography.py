"""Cryptographic operations used across the Rekono platform.

Provides the Crypto class, which wraps Fernet symmetric encryption for values
that must be recovered later, SHA-512 hashing for values that only need to be
verified (such as API tokens and OTP codes), and secure random string
generation backed by the `secrets` module.
"""

import hashlib
import secrets
import string
from dataclasses import dataclass
from functools import cached_property

from cryptography.fernet import Fernet


@dataclass
class Crypto:
    """Encryption, hashing, and random generation for the Rekono secrets.

    Attributes:
        encryption_key: Base64-encoded Fernet key used to derive the signing and
            encryption keys. This class does not read configuration or generate a key on
            its own: callers are expected to supply CONFIG.encryption_key and to avoid
            constructing Crypto at all when no key is configured, since encrypt/decrypt
            require a valid key to work.
    """

    encryption_key: str

    @cached_property
    def fernet(self) -> Fernet:
        """The Fernet instance built from the encryption key on first access.

        Fernet validates the key format itself, so an encryption_key that isn't a
        valid base64-encoded 32-byte key raises here rather than when the Crypto
        instance is created.
        """
        return Fernet(self.encryption_key.encode())

    def encrypt(self, value: str) -> str:
        """Encrypt a value with the encryption key.

        Args:
            value: Plain value to protect.

        Returns:
            URL-safe base64-encoded Fernet token, containing the ciphertext, a
            timestamp, and an HMAC-SHA256 authentication tag.
        """
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        """Decrypt a value previously produced by encrypt().

        Verifies the token's HMAC-SHA256 authentication tag before returning the
        plaintext value, so corrupted or tampered tokens are rejected. No TTL is
        passed to Fernet, so the token's embedded timestamp is not checked and
        encrypted values never expire.

        Args:
            value: Fernet token returned by encrypt.

        Returns:
            The original plain value.

        Raises:
            InvalidToken: If decryption fails due to invalid key, corrupted data, or tampering.
        """
        return self.fernet.decrypt(value.encode()).decode()

    @classmethod
    def generate_encryption_key(cls) -> str:
        """Generate a new base64-encoded Fernet encryption key.

        Returns:
            A key ready to be configured as the Rekono encryption key.
        """
        return Fernet.generate_key().decode()

    @classmethod
    def hash(cls, value: str) -> str:
        """Hash a value with SHA-512, without salt.

        Used for high-entropy values that only need to be verified by comparison,
        such as API tokens and OTP codes, and never for user passwords, which are
        hashed by Django with its own password hashers.

        Args:
            value: High-entropy value to hash.

        Returns:
            The hash as a hexadecimal string, which is what gets stored.
        """
        return hashlib.sha512(value.encode()).hexdigest()

    @classmethod
    def random(cls, size: int) -> str:
        """Generate a random value of the given length.

        Picks each character using secrets.choice from string.printable, which
        includes digits, ASCII letters, punctuation, and whitespace characters
        (space, tab, newline, carriage return, form feed, vertical tab).

        Args:
            size: Number of characters of the generated value.

        Returns:
            The random value, which may contain whitespace and therefore has to be
            hashed or encrypted rather than compared after being trimmed.
        """
        return "".join(secrets.choice(string.printable) for _ in range(size))
