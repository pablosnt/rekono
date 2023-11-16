import hashlib


def hash(value: str) -> str:
    """Calculate the hash value from a plain value using the SHA-512 algorithm.

    Args:
        value (str): Plain value

    Returns:
        str: Hash value
    """
    return hashlib.sha512(value.encode()).hexdigest()
