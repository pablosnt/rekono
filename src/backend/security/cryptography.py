import hashlib
import secrets
import string
from dataclasses import dataclass
from functools import cached_property

from cryptography.fernet import Fernet


@dataclass
class Crypto:
    encryption_key: str

    @cached_property
    def fernet(self) -> Fernet:
        return Fernet(self.encryption_key.encode())

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()

    @classmethod
    def generate_encryption_key(cls) -> str:
        return Fernet.generate_key().decode()

    @classmethod
    def hash(cls, value: str) -> str:
        return hashlib.sha512(value.encode()).hexdigest()

    @classmethod
    def random(cls, size: int) -> str:
        return "".join(secrets.choice(string.printable) for _ in range(size))
