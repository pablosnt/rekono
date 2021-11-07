import hashlib
import secrets
import string


def generate_random_value(size: int) -> str:
    return ''.join(secrets.choice(string.printable) for _ in range(size))


def hash(value: str) -> str:
    return hashlib.sha512(value.encode()).hexdigest()


def generate_otp() -> str:
    return hash(generate_random_value(3000))
