"""Cryptographic utilities for the Rekono platform.

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
    """Cryptographic utility class for reversible encryption, one-way hashing, and random generation.

    Wraps the `cryptography` package's Fernet implementation for symmetric encryption,
    exposes SHA-512 hashing for values that are only ever compared rather than recovered,
    and generates cryptographically secure random strings. This class serves as the
    central cryptographic service for the Rekono platform.

    Security Features:
        - Fernet symmetric encryption (AES-128 in CBC mode with PKCS7 padding, authenticated
          with HMAC-SHA256) for values such as stored integration secrets that must be
          decrypted later
        - Unsalted SHA-512 hashing for high-entropy values that only need to be verified,
          such as API tokens and OTP codes, never for low-entropy user passwords
        - CSPRNG-backed random string generation via `secrets.choice`

    Attributes:
        encryption_key (str): Base64-encoded Fernet key used to derive the signing and
            encryption keys. This class does not read configuration or generate a key on
            its own: callers are expected to supply CONFIG.encryption_key and to avoid
            constructing Crypto at all when no key is configured, since encrypt/decrypt
            require a valid key to work.

    Example:
        Initialize and use cryptographic operations:

        ```python
        crypto = Crypto(encryption_key="your-base64-key")
        encrypted = crypto.encrypt("sensitive data")
        decrypted = crypto.decrypt(encrypted)
        hashed = Crypto.hash("api-token")
        random_token = Crypto.random(32)
        ```
    """

    encryption_key: str

    @cached_property
    def fernet(self) -> Fernet:
        """Get the Fernet instance built from the configured encryption key.

        Builds the Fernet instance from encryption_key on first access and reuses it
        for subsequent calls. Fernet validates the key format itself, so an
        encryption_key that isn't a valid base64-encoded 32-byte key raises here
        rather than when the Crypto instance is created.

        Returns:
            Fernet: Fernet instance for symmetric operations.
        """
        return Fernet(self.encryption_key.encode())

    def encrypt(self, value: str) -> str:
        """Encrypt a string value using Fernet symmetric encryption.

        Args:
            value (str): The plaintext string to encrypt.

        Returns:
            str: URL-safe base64-encoded Fernet token, containing the ciphertext,
                a timestamp, and an HMAC-SHA256 authentication tag.
        """
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        """Decrypt a value previously produced by encrypt().

        Verifies the token's HMAC-SHA256 authentication tag before returning the
        plaintext value, so corrupted or tampered tokens are rejected. No TTL is
        passed to Fernet, so the token's embedded timestamp is not checked and
        encrypted values never expire.

        Args:
            value (str): URL-safe base64-encoded Fernet token to decrypt.

        Returns:
            str: Decrypted plaintext string.

        Raises:
            InvalidToken: If decryption fails due to invalid key, corrupted data, or tampering.
        """
        return self.fernet.decrypt(value.encode()).decode()

    @classmethod
    def generate_encryption_key(cls) -> str:
        """Generate a new Fernet encryption key.

        Creates a new cryptographically secure encryption key suitable for
        Fernet symmetric encryption. The key is generated using secure
        random number generation and encoded as base64 for storage.

        Returns:
            str: Base64-encoded Fernet encryption key (44 characters).
        """
        return Fernet.generate_key().decode()

    @classmethod
    def hash(cls, value: str) -> str:
        """Hash a string using SHA-512.

        Computes an unsalted SHA-512 hash of the input string. This is used for
        high-entropy values that only need to be verified by comparison, such as
        API tokens and OTP codes, not for low-entropy user passwords.

        Args:
            value (str): The string value to hash.

        Returns:
            str: Hexadecimal SHA-512 hash digest (128 characters).
        """
        return hashlib.sha512(value.encode()).hexdigest()

    @classmethod
    def random(cls, size: int) -> str:
        """Generate a cryptographically secure random string.

        Picks each character using secrets.choice from string.printable, which
        includes digits, ASCII letters, punctuation, and whitespace characters
        (space, tab, newline, carriage return, form feed, vertical tab).

        Args:
            size (int): The desired length of the random string.

        Returns:
            str: Cryptographically secure random string of specified length.
        """
        return "".join(secrets.choice(string.printable) for _ in range(size))
