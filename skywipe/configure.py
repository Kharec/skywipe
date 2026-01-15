"""Core configuration module for Skywipe"""

from getpass import getpass
import re
from pathlib import Path
from typing import NamedTuple
import yaml
from .logger import setup_logger


class ValidationResult(NamedTuple):
    is_valid: bool
    error_message: str


def _validate_handle(handle: str) -> ValidationResult:
    if not handle:
        return ValidationResult(False, "Handle cannot be empty")

    if len(handle) > 253:
        return ValidationResult(False, "Handle is too long (max 253 characters)")

    if " " in handle:
        return ValidationResult(False, "Handle cannot contain spaces")

    handle_pattern = re.compile(
        r"^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$|"
        r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$|"
        r"^did:[a-z]+:[a-zA-Z0-9._-]+$"
    )

    if not handle_pattern.match(handle):
        return ValidationResult(False, (
            "Invalid handle format. "
            "Use a username (e.g., 'alice'), full handle (e.g., 'alice.bsky.social'), "
            "or DID (e.g., 'did:plc:...')"
        ))

    return ValidationResult(True, "")


def _validate_password(password: str) -> ValidationResult:
    if not password:
        return ValidationResult(False, "Password cannot be empty")

    if len(password) < 8:
        return ValidationResult(False, "Password is too short (minimum 8 characters)")

    return ValidationResult(True, "")


class Configuration:
    def __init__(self):
        self.config_file = Path.home() / ".config" / "skywipe" / "config.yml"

    def exists(self) -> bool:
        return self.config_file.exists()

    def _confirm_overwrite(self, logger) -> bool:
        if not self.exists():
            return True
        overwrite = input(
            "Configuration already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite in ("y", "yes"):
            return True
        logger.info("Configuration creation cancelled.")
        return False

    def _ensure_config_dir(self) -> None:
        config_dir = self.config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)

    def _prompt_handle(self, logger) -> str:
        while True:
            handle = input("Bluesky handle: ").strip()
            is_valid, error_msg = _validate_handle(handle)
            if is_valid:
                return handle
            logger.error(error_msg)
            logger.info("Please enter a valid handle and try again.")

    def _prompt_password(self, logger) -> str:
        while True:
            password = getpass(
                "Bluesky (hopefully app) password: ").strip()
            is_valid, error_msg = _validate_password(password)
            if is_valid:
                return password
            logger.error(error_msg)
            logger.info("Please check your password and try again.")
            logger.info(
                "Generate an app password at: https://bsky.app/settings/app-passwords")

    def _parse_batch_size(self, logger) -> int | None:
        batch_size = input("Batch size (default: 10): ").strip() or "10"
        try:
            batch_size_int = int(batch_size)
        except ValueError:
            logger.error("batch_size must be an integer")
            return None
        if batch_size_int < 1 or batch_size_int > 100:
            logger.error("batch_size must be between 1 and 100")
            return None
        return batch_size_int

    def _parse_delay(self, logger) -> int | None:
        delay = input(
            "Delay between batches in seconds (default: 1): ").strip() or "1"
        try:
            delay_int = int(delay)
        except ValueError:
            logger.error("delay must be an integer")
            return None
        if delay_int < 0 or delay_int > 60:
            logger.error("delay must be between 0 and 60 seconds")
            return None
        return delay_int

    def _parse_verbose(self) -> bool:
        verbose_input = input(
            "Verbose mode (y/n, default: y): ").strip().lower() or "y"
        return verbose_input in ("y", "yes", "true", "1")

    def _write_config(self, logger, config_data: dict) -> None:
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save configuration: {e}")
            return
        logger.info(f"Configuration saved to {self.config_file}")

    def create(self):
        logger = setup_logger(verbose=False)
        if not self._confirm_overwrite(logger):
            return

        self._ensure_config_dir()

        print("Skywipe Configuration")
        print("=" * 50)
        print("Note: You should use an app password from Bluesky settings.")

        handle = self._prompt_handle(logger)
        password = self._prompt_password(logger)
        batch_size = self._parse_batch_size(logger)
        if batch_size is None:
            return
        delay = self._parse_delay(logger)
        if delay is None:
            return
        verbose = self._parse_verbose()

        config_data = {
            "handle": handle,
            "password": password,
            "batch_size": batch_size,
            "delay": delay,
            "verbose": verbose
        }

        self._write_config(logger, config_data)

    def load(self) -> dict:
        if not self.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}")
        try:
            with open(self.config_file, "r") as f:
                config_data = yaml.safe_load(f)
                if config_data is None:
                    raise ValueError("Configuration file is empty or invalid")
                return config_data
        except (IOError, OSError) as e:
            raise ValueError(
                f"Failed to read configuration file: {e}") from e
        except yaml.YAMLError as e:
            raise ValueError(
                f"Invalid YAML in configuration file: {e}") from e
