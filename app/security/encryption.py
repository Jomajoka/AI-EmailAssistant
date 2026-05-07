import os
from functools import lru_cache

from cryptography.fernet import Fernet


ENCRYPTED_PREFIX = "enc:v1:"


class EncryptionConfigError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key = os.getenv("EMAIL_ENCRYPTION_KEY")

    if not key:
        raise EncryptionConfigError("EMAIL_ENCRYPTION_KEY is required")

    try:
        return Fernet(key.encode("utf-8"))
    except Exception as exc:
        raise EncryptionConfigError("EMAIL_ENCRYPTION_KEY must be a valid Fernet key") from exc


def validate_encryption_config() -> None:
    _get_fernet()


def is_encrypted(value: str | None) -> bool:
    return isinstance(value, str) and value.startswith(ENCRYPTED_PREFIX)


def encrypt_value(value: str | None) -> str | None:
    if value is None or is_encrypted(value):
        return value

    token = _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{ENCRYPTED_PREFIX}{token}"


def decrypt_value(value: str | None) -> str | None:
    if value is None or not is_encrypted(value):
        return value

    token = value[len(ENCRYPTED_PREFIX):]
    return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
