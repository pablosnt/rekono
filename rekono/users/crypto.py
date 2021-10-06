import string
import secrets
import hashlib


def generate_random_value(size: int) -> str:
    return ''.join(secrets.choice(string.printable) for i in range(size))


def generate_otp() -> str:
    return hashlib.sha512(generate_random_value(3000).encode()).hexdigest()
