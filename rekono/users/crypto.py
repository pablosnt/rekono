import string
import secrets
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings


def generate_random_value(size: int) -> str:
    return ''.join(secrets.choice(string.printable) for i in range(size))


def hash(value: str) -> str:
    return hashlib.sha512(value.encode()).hexdigest()


def generate_otp() -> str:
    return hash(generate_random_value(3000))


def encrypt(plain_text: str) -> str:
    key = settings.ENCRYPTION_KEY[:32].encode()
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    encrypted = base64.b64encode(encrypted_bytes).decode()
    return f'{iv}:{encrypted}'


def decrypt(encrypted: str) -> str:
    aux = encrypted.split(':', 1)
    iv = base64.b64decode(aux[0])
    encrypted_text = base64.b64decode(aux[1])
    key = settings.ENCRYPTION_KEY[:32].encode()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(encrypted_text), AES.block_size)
    return plain_text
