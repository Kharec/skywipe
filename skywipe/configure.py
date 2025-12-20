"""Core configuration module for Skywipe"""

import getpass
from pathlib import Path
import yaml
from .logger import setup_logger


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
            logger.error("batch_size and delay must be integers")
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
