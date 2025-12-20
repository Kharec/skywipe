"""Authentication module for Skywipe"""

from atproto import Client
from .configure import Configuration


class Auth:
    def __init__(self):
        self.config = Configuration()
        self.client = None

    def login(self) -> Client:
        try:
            config_data = self.config.load()
        except FileNotFoundError as e:
            raise ValueError(
                "Configuration file not found. Run 'skywipe configure' first.") from e

        handle = config_data.get("handle")
        password = config_data.get("password")

        if not handle or not password:
            raise ValueError(
                "handle and password must be set in configuration")

        try:
            self.client = Client()
            self.client.login(handle, password)
        except Exception as e:
            raise ValueError(
                f"Failed to authenticate: {e}") from e

        return self.client
