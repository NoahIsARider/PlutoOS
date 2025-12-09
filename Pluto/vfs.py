"""
Virtual File System (VFS) for Pluto userland. Stores files encrypted using PrivacyVault.
"""
import os
from pathlib import Path
from Pluto.privacy import PrivacyVault


class VFS:
    def __init__(self, storage_dir='vault/vfs', key_path='vault/key.key'):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.vault = PrivacyVault(key_path=key_path, storage_dir=self.storage_dir)

    def _blob_name(self, path: str) -> str:
        # simple mapping: sanitize path
        p = path.strip('/').replace('/', '__') or 'root'
        return p

    def write(self, path: str, data: bytes):
        name = self._blob_name(path)
        self.vault.store(name, data)

    def read(self, path: str) -> bytes:
        name = self._blob_name(path)
        return self.vault.retrieve(name)

    def ls(self, prefix: str = ''):
        # list stored blobs that match prefix
        pfx = prefix.strip('/').replace('/', '__')
        files = []
        for f in Path(self.storage_dir).glob('*.dat'):
            n = f.stem
            # normalize display: replace __ -> / and strip trailing .dat if present
            display = n.replace('__', '/')
            if display.endswith('.dat'):
                display = display[:-4]
            if pfx == '' or n.startswith(pfx):
                files.append(display)
        # deduplicate and return
        seen = []
        for x in files:
            if x not in seen:
                seen.append(x)
        return seen

    def rm(self, path: str):
        name = self._blob_name(path)
        # Try removing common variants created by past bugs: name.dat and name.dat.dat
        removed = False
        for candidate in (f"{name}.dat", f"{name}.dat.dat"):
            full = os.path.join(self.storage_dir, candidate)
            if os.path.exists(full):
                os.remove(full)
                removed = True
        if not removed:
            raise FileNotFoundError(path)
