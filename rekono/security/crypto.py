import string
import secrets
import hashlib
import base64
import json
from Crypto.Cipher import AES
from django.conf import settings


def generate_random_value(size: int) -> str:
    return ''.join(secrets.choice(string.printable) for i in range(size))


def hash(value: str) -> str:
    return hashlib.sha512(value.encode()).hexdigest()


def generate_otp() -> str:
    return hash(generate_random_value(3000))


def encrypt(plaintext: str) -> str:
    key = settings.ENCRYPTION_KEY[:32].encode()
    header = generate_random_value(100)
    cipher = AES.new(key, AES.MODE_GCM)
    cipher.update(header.encode())
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    output = {
        'nonce': base64.b64encode(cipher.nonce).decode(),
        'header': base64.b64encode(header.encode()).decode(),
        'ciphertext': base64.b64encode(ciphertext).decode(),
        'tag': base64.b64encode(tag).decode()
    }
    return base64.b64encode(json.dumps(output).encode()).decode()


def decrypt(encrypted: str) -> str:
    data = json.loads(base64.b64decode(encrypted.encode()).decode())
    key = settings.ENCRYPTION_KEY[:32].encode()
    cipher = AES.new(key, AES.MODE_GCM, nonce=base64.b64decode(data['nonce']))
    cipher.update(base64.b64decode(data['header']))
    plaintext = cipher.decrypt_and_verify(
        base64.b64decode(data['ciphertext']),
        base64.b64decode(data['tag'])
    )
    return plaintext
