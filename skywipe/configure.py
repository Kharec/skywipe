"""Core configuration module for Skywipe"""

import getpass
import re
from pathlib import Path
import yaml
from .logger import setup_logger


def _validate_handle(handle: str) -> tuple[bool, str]:
    if not handle:
        return False, "Handle cannot be empty"

    if len(handle) > 253:
        return False, "Handle is too long (max 253 characters)"

    if " " in handle:
        return False, "Handle cannot contain spaces"

    handle_pattern = re.compile(
        r"^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$|"
        r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$|"
        r"^did:[a-z]+:[a-zA-Z0-9._-]+$"
    )

    if not handle_pattern.match(handle):
        return False, (
            "Invalid handle format. "
            "Use a username (e.g., 'alice'), full handle (e.g., 'alice.bsky.social'), "
            "or DID (e.g., 'did:plc:...')"
        )

    return True, ""


def _validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Password cannot be empty"

    if len(password) < 8:
        return False, "Password is too short (minimum 8 characters)"

    return True, ""


class Configuration:
    def __init__(self):
        self.config_file = Path.home() / ".config" / "skywipe" / "config.yml"

    def exists(self) -> bool:
        return self.config_file.exists()

    def create(self):
        logger = setup_logger(verbose=False)
        if self.exists():
            overwrite = input(
                "Configuration already exists. Overwrite? (y/N): ").strip().lower()
            if overwrite not in ("y", "yes"):
                logger.info("Configuration creation cancelled.")
                return

        config_dir = self.config_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        print("Skywipe Configuration")
        print("=" * 50)
        print("Note: You should use an app password from Bluesky settings.")

        while True:
            handle = input("Bluesky handle: ").strip()
            is_valid, error_msg = _validate_handle(handle)
            if is_valid:
                break
            logger.error(error_msg)
            logger.info("Please enter a valid handle and try again.")

        while True:
            password = getpass.getpass(
                "Bluesky (hopefully app) password: ").strip()
            is_valid, error_msg = _validate_password(password)
            if is_valid:
                break
            logger.error(error_msg)
            logger.info("Please check your password and try again.")
            logger.info(
                "Generate an app password at: https://bsky.app/settings/app-passwords")

        batch_size = input("Batch size (default: 10): ").strip() or "10"
        delay = input(
            "Delay between batches in seconds (default: 1): ").strip() or "1"
        verbose_input = input(
            "Verbose mode (y/n, default: y): ").strip().lower() or "y"
        verbose = verbose_input in ("y", "yes", "true", "1")

        try:
            batch_size = int(batch_size)
            if batch_size < 1 or batch_size > 100:
                logger.error("batch_size must be between 1 and 100")
                return
        except ValueError:
            logger.error("batch_size must be an integer")
            return

        try:
            delay = int(delay)
            if delay < 0 or delay > 60:
                logger.error("delay must be between 0 and 60 seconds")
                return
        except ValueError:
            logger.error("delay must be an integer")
            return

        config_data = {
            "handle": handle,
            "password": password,
            "batch_size": batch_size,
            "delay": delay,
            "verbose": verbose
        }

        try:
            with open(self.config_file, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save configuration: {e}")
            return

        logger.info(f"Configuration saved to {self.config_file}")

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
