from cryptography.fernet import Fernet
from django.conf import settings


class EncryptionService:
    f = Fernet(settings.ENCRYPTION_KEY.encode())

    @staticmethod
    def encrypt(value: str) -> str:
        return EncryptionService.f.encrypt(value.encode()).decode()

    @staticmethod
    def decrypt(value: str) -> str:
        return EncryptionService.f.decrypt(value.encode()).decode()
