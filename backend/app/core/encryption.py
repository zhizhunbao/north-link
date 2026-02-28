"""AES-256 encryption/decryption for sensitive merchant fields."""

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from app.config import settings

# AES block size = 128 bits = 16 bytes
BLOCK_SIZE = 128


def _get_key() -> bytes:
    """Get 32-byte encryption key from settings."""
    key = settings.encryption_key.encode("utf-8")
    # Pad or truncate to exactly 32 bytes
    return key[:32].ljust(32, b"\0")


def encrypt(plaintext: str) -> bytes:
    """Encrypt a string using AES-256-CBC. Returns raw bytes for BYTEA storage."""
    if not plaintext:
        return b""
    key = _get_key()
    iv = os.urandom(16)

    padder = PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(plaintext.encode("utf-8")) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Prepend IV to ciphertext for storage
    return iv + ciphertext


def decrypt(data: bytes) -> str:
    """Decrypt AES-256-CBC encrypted bytes back to string."""
    if not data:
        return ""
    key = _get_key()

    # Extract IV (first 16 bytes) and ciphertext
    iv = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = PKCS7(BLOCK_SIZE).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()

    return plaintext.decode("utf-8")
