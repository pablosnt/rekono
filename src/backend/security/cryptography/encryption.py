from cryptography.fernet import Fernet
from rekono.settings import CONFIG


class Encryption:
    fernet = Fernet(CONFIG.encryption_key.encode())

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()
