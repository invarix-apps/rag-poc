import base64
import os
import uuid
from dataclasses import dataclass
from functools import lru_cache

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import get_settings
from app.errors import (
    InvalidEncryptionKeyError,
    SecretDecryptionError,
    SecretEncryptionUnavailableError,
)

NONCE_SIZE = 12
KEY_SIZE = 32


@dataclass(frozen=True, kw_only=True)
class Keyring:
    active: str
    keys: dict[str, bytes]

    def get(self, version: str) -> bytes:
        key = self.keys.get(version)
        if key is None:
            raise SecretDecryptionError()
        return key


@lru_cache
def get_keyring() -> Keyring:
    raw = get_settings().encryption_keys
    if not raw:
        raise SecretEncryptionUnavailableError()

    keys: dict[str, bytes] = {}
    order: list[str] = []
    for entry in raw.split(","):
        version, _, encoded = entry.strip().partition(":")
        if not version or not encoded:
            raise InvalidEncryptionKeyError()
        try:
            key = base64.urlsafe_b64decode(encoded)
        except ValueError as exc:
            raise InvalidEncryptionKeyError() from exc
        if len(key) != KEY_SIZE:
            raise InvalidEncryptionKeyError()
        keys[version] = key
        order.append(version)

    if not order:
        raise InvalidEncryptionKeyError()
    return Keyring(active=order[0], keys=keys)


def build_aad(provider_id: uuid.UUID, api_key_id: uuid.UUID) -> bytes:
    return f"{provider_id}:{api_key_id}".encode()


def seal(secret: str, provider_id: uuid.UUID, api_key_id: uuid.UUID) -> str:
    keyring = get_keyring()
    nonce = os.urandom(NONCE_SIZE)
    sealed = AESGCM(keyring.keys[keyring.active]).encrypt(
        nonce, secret.encode(), build_aad(provider_id, api_key_id)
    )
    payload = base64.urlsafe_b64encode(nonce + sealed).decode()
    return f"{keyring.active}:{payload}"


def unseal(blob: str, provider_id: uuid.UUID, api_key_id: uuid.UUID) -> str:
    version, _, payload = blob.partition(":")
    if not payload:
        raise SecretDecryptionError()

    key = get_keyring().get(version)
    try:
        raw = base64.urlsafe_b64decode(payload)
        secret = AESGCM(key).decrypt(
            raw[:NONCE_SIZE], raw[NONCE_SIZE:], build_aad(provider_id, api_key_id)
        )
    except (InvalidTag, ValueError) as exc:
        raise SecretDecryptionError() from exc
    return secret.decode()


def generate_key() -> str:
    return base64.urlsafe_b64encode(os.urandom(KEY_SIZE)).decode()
