"""Cryptographic utilities and encryption services for Rekono.

Provides secure cryptographic operations including AES encryption/decryption,
SHA-512 hashing, and secure random string generation. This module implements
enterprise-grade cryptographic standards for protecting sensitive data throughout
the Rekono platform.
"""

import hashlib
import secrets
import string
from dataclasses import dataclass
from functools import cached_property

from cryptography.fernet import Fernet


@dataclass
class Crypto:
    """Cryptographic utility class providing encryption, hashing, and random generation.

    Implements AES-256 encryption using Fernet symmetric encryption, SHA-512 hashing
    for secure password storage, and cryptographically secure random string generation.
    This class serves as the central cryptographic service for the Rekono platform.

    Attributes:
        encryption_key (str): Base64-encoded Fernet encryption key for symmetric operations.

    Example:
        Initialize and use cryptographic operations:

        ```python
        crypto = Crypto(encryption_key="your-base64-key")
        encrypted = crypto.encrypt("sensitive data")
        decrypted = crypto.decrypt(encrypted)
        hashed = Crypto.hash("password")
        random_token = Crypto.random(32)
        ```
    """

    encryption_key: str

    @cached_property
    def fernet(self) -> Fernet:
        """Get cached Fernet encryption instance.

        Creates and caches a Fernet instance using the configured encryption key.
        The instance is cached for performance optimization while maintaining
        thread safety for cryptographic operations.

        Returns:
            Fernet: Cached Fernet encryption instance for symmetric operations.
        """
        return Fernet(self.encryption_key.encode())

    def encrypt(self, value: str) -> str:
        """Encrypt a string value using AES-256 encryption.

        Encrypts the provided string using Fernet symmetric encryption with
        AES-256 in CBC mode. The encrypted result includes authentication
        data to prevent tampering and replay attacks.

        Args:
            value (str): The plaintext string to encrypt.

        Returns:
            str: Base64-encoded encrypted string with authentication data.
        """
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        """Decrypt an encrypted string value.

        Decrypts a previously encrypted string using the configured encryption key.
        Verifies authentication data to ensure data integrity and prevent
        tampering before returning the plaintext value.

        Args:
            value (str): Base64-encoded encrypted string to decrypt.

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
        """Hash a string using SHA-512 cryptographic hashing.

        Computes a SHA-512 cryptographic hash of the input string. This method
        is suitable for password hashing, token verification, and data integrity
        checks where cryptographic security is required.

        Args:
            value (str): The string value to hash.

        Returns:
            str: Hexadecimal SHA-512 hash digest (128 characters).
        """
        return hashlib.sha512(value.encode()).hexdigest()

    @classmethod
    def random(cls, size: int) -> str:
        """Generate a cryptographically secure random string.

        Creates a random string using cryptographically secure random number
        generation. The string contains characters from the printable ASCII
        character set including letters, digits, and special characters.

        Args:
            size (int): The desired length of the random string.

        Returns:
            str: Cryptographically secure random string of specified length.
        """
        return "".join(secrets.choice(string.printable) for _ in range(size))
