"""Authentication module for Skywipe CLI."""

from atproto import Client
from skywipe.configure import Configuration


class Auth:
    def __init__(self, configuration: Configuration = None):
        self.configuration = configuration or Configuration()
        self.client: Client = None

    def login(self) -> Client:
        config_data = self.configuration.load()

        handle = config_data.get("handle")
        password = config_data.get("password")

        if not handle or not password:
            raise ValueError(
                "handle and password must be set in configuration")

        self.client = Client()
        self.client.login(handle, password)

        return self.client
