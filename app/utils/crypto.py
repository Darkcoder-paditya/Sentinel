import base64
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_aes_key() -> bytes:
    # Derive a 32-byte key from env secret or random fallback
    secret = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret").encode()
    # Simple derivation for local use; replace with HKDF if needed
    padded = (secret * 32)[:32]
    return padded


def encrypt_to_b64(plaintext: str) -> str:
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt_from_b64(token: str) -> str:
    raw = base64.b64decode(token)
    nonce, ct = raw[:12], raw[12:]
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode()
