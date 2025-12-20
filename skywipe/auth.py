"""Authentication module for Skywipe"""

from atproto import Client
from .configure import Configuration


class Auth:
    def __init__(self):
        self.config = Configuration()
        self.client = None

    def login(self) -> Client:
        config_data = self.config.load()

        handle = config_data.get("handle")
        password = config_data.get("password")

        if not handle or not password:
            raise ValueError(
                "handle and password must be set in configuration")

        self.client = Client()
        self.client.login(handle, password)

        return self.client
