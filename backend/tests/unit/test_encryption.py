"""Unit tests for core/encryption.py — AES-256-CBC encrypt/decrypt."""

import os

import pytest

os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-32bytes!!")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/northlink_test",
)

from app.core.encryption import decrypt, encrypt  # noqa: E402


class TestEncryptDecrypt:
    """Tests for AES-256-CBC encrypt/decrypt round-trip."""

    def test_encrypt_returns_bytes(self):
        result = encrypt("hello")
        assert isinstance(result, bytes)

    def test_encrypt_non_empty_produces_ciphertext_longer_than_16_bytes(self):
        # IV (16) + at least one block (16)
        result = encrypt("hello")
        assert len(result) > 16

    def test_different_calls_produce_different_ciphertext(self):
        # IV is random, so ciphertext should differ
        c1 = encrypt("hello")
        c2 = encrypt("hello")
        assert c1 != c2

    def test_decrypt_after_encrypt_returns_original(self):
        plaintext = "test-phone-number"
        ciphertext = encrypt(plaintext)
        assert decrypt(ciphertext) == plaintext

    def test_empty_string_encrypt_returns_empty_bytes(self):
        assert encrypt("") == b""

    def test_empty_bytes_decrypt_returns_empty_string(self):
        assert decrypt(b"") == ""

    def test_unicode_round_trip(self):
        plaintext = "北京市朝阳区"
        assert decrypt(encrypt(plaintext)) == plaintext

    def test_long_string_round_trip(self):
        plaintext = "A" * 500
        assert decrypt(encrypt(plaintext)) == plaintext

    def test_special_chars_round_trip(self):
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        assert decrypt(encrypt(plaintext)) == plaintext
