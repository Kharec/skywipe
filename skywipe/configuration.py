"""Core configuration handling class and related logic."""

import os
import getpass
from pathlib import Path
import yaml
from cryptography.fernet import Fernet


class Configuration:
    def __init__(self):
        self.config_file = Path.home() / ".config" / "skywipe" / "config.yml"
        self.key_file = Path.home() / ".config" / "skywipe" / ".key"
        self._fernet = None

    def exists(self) -> bool:
        return self.config_file.exists()

    def _get_or_create_key(self) -> bytes:
        if self.key_file.exists():
            return self.key_file.read_bytes()

        key = Fernet.generate_key()
        config_dir = self.key_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        self.key_file.write_bytes(key)
        os.chmod(self.key_file, 0o600)
        return key

    def _get_fernet(self) -> Fernet:
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet

    def encrypt_password(self, password: str) -> str:
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(password.encode())
        return encrypted.decode()

    def decrypt_password(self, encrypted_password: str) -> str:
        fernet = self._get_fernet()
        decrypted = fernet.decrypt(encrypted_password.encode())
        return decrypted.decode()

    def create(self):
        if self.exists():
            overwrite = input(
                "Configuration already exists. Overwrite? (y/N): ").strip().lower()
            if overwrite not in ("y", "yes"):
                return

        config_dir = self.config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        print("Skywipe Configuration")
        print("=" * 50)
        handle = input("Bluesky handle: ").strip()
        password = getpass.getpass("Bluesky app password: ").strip()
        batch_size = input("Batch size (default: 10): ").strip() or "10"
        delay = input(
            "Delay between batches in seconds (default: 1): ").strip() or "1"
        verbose_input = input(
            "Verbose mode (y/n, default: y): ").strip().lower() or "y"
        verbose = verbose_input in ("y", "yes", "true", "1")

        try:
            batch_size = int(batch_size)
            delay = int(delay)
        except ValueError:
            print("Error: batch_size and delay must be integers")
            return

        encrypted_password = self.encrypt_password(password)

        config_data = {
            "handle": handle,
            "password": encrypted_password,
            "batch_size": batch_size,
            "delay": delay,
            "verbose": verbose
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

        print(f"\nConfiguration saved to {self.config_file}")
