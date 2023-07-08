import hashlib
import secrets
import string


def generate_random_value(size: int) -> str:
    '''Generate a secure random value.

    Args:
        size (int): Size of the secure random value

    Returns:
        str: Secure random value
    '''
    return ''.join(secrets.choice(string.printable) for _ in range(size))


def hash(value: str) -> str:
    '''Calculate the hash value from a plain value using the SHA-512 algorithm.

    Args:
        value (str): Plain value

    Returns:
        str: Hash value
    '''
    return hashlib.sha512(value.encode()).hexdigest()
