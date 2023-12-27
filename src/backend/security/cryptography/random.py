import secrets
import string


def generate_random_value(size: int) -> str:
    """Generate a secure random value.

    Args:
        size (int): Size of the secure random value

    Returns:
        str: Secure random value
    """
    return "".join(secrets.choice(string.printable) for _ in range(size))
