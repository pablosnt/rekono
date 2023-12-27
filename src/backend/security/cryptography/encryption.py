from cryptography.fernet import Fernet


class Encryptor:
    def __init__(self, encryption_key: str) -> None:
        self.fernet = Fernet(encryption_key.encode())

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()

    @classmethod
    def generate_encryption_key(self) -> str:
        return Fernet.generate_key().decode()
