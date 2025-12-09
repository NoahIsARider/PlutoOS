"""
Privacy Vault for PlutoOS — stores secrets encrypted on disk.
Uses `cryptography.Fernet` when available; falls back to a simple XOR for demo.
"""
import os
import base64
import warnings

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False

class PrivacyVault:
    def __init__(self, key_path='vault/key.key', storage_dir='vault/data'):
        self.key_path = key_path
        self.storage_dir = storage_dir
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
        os.makedirs(self.storage_dir, exist_ok=True)

        if HAS_CRYPTO:
            if not os.path.exists(self.key_path):
                k = Fernet.generate_key()
                with open(self.key_path, 'wb') as f:
                    f.write(k)
            self.key = open(self.key_path, 'rb').read()
            self.cipher = Fernet(self.key)
        else:
            warnings.warn('cryptography not available — using fallback XOR cipher (demo only)')
            if not os.path.exists(self.key_path):
                with open(self.key_path, 'wb') as f:
                    f.write(b'pluto-fallback-key-16')
            self.key = open(self.key_path, 'rb').read()

    def encrypt(self, data: bytes) -> bytes:
        if HAS_CRYPTO:
            return self.cipher.encrypt(data)
        else:
            return self._xor(data)

    def decrypt(self, token: bytes) -> bytes:
        if HAS_CRYPTO:
            return self.cipher.decrypt(token)
        else:
            return self._xor(token)

    def store(self, name: str, data: bytes):
        """Store encrypted blob as `storage_dir/{name}.dat`."""
        token = self.encrypt(data)
        path = os.path.join(self.storage_dir, f"{name}.dat")
        with open(path, 'wb') as f:
            f.write(token)

    def retrieve(self, name: str) -> bytes:
        path = os.path.join(self.storage_dir, f"{name}.dat")
        if not os.path.exists(path):
            raise KeyError(name)
        with open(path, 'rb') as f:
            return self.decrypt(f.read())

    def _xor(self, data: bytes) -> bytes:
        k = self.key
        return bytes(b ^ k[i % len(k)] for i, b in enumerate(data))
