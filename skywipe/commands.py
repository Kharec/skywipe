"""Command implementations for Skywipe"""

from typing import Callable, Dict, Optional
from .configure import Configuration
from .posts import delete_posts
from .medias import delete_posts_with_medias
from .likes import undo_likes


CommandHandler = Callable[[], None]


class CommandRegistry:
    def __init__(self):
        self._commands = {}
        self._help_texts = {}
        self._requires_config = {}

    def register(
        self,
        name: str,
        handler: CommandHandler,
        help_text: str,
        requires_config: bool = True
    ):
        self._commands[name] = handler
        self._help_texts[name] = help_text
        self._requires_config[name] = requires_config

    def get_handler(self, name: str) -> Optional[CommandHandler]:
        return self._commands.get(name)

    def get_help_text(self, name: str) -> Optional[str]:
        return self._help_texts.get(name)

    def requires_config(self, name: str) -> bool:
        return self._requires_config.get(name, True)

    def get_all_commands(self) -> Dict[str, str]:
        return self._help_texts.copy()

    def execute(self, name: str):
        handler = self.get_handler(name)
        if handler:
            handler()
        else:
            raise ValueError(f"Unknown command: {name}")


registry = CommandRegistry()


def run_configure():
    config = Configuration()
    config.create()


def run_posts():
    delete_posts()


def run_medias():
    delete_posts_with_medias()


def run_likes():
    undo_likes()


def run_reposts():
    print("Command 'reposts' is not yet implemented.")


def run_quotes():
    print("Command 'quotes' is not yet implemented.")


def run_follows():
    print("Command 'follows' is not yet implemented.")


def run_bookmarks():
    print("Command 'bookmarks' is not yet implemented")


def run_all():
    registry.execute("posts")
    registry.execute("medias")
    registry.execute("likes")
    registry.execute("reposts")
    registry.execute("quotes")
    registry.execute("follows")
    registry.execute("bookmarks")


registry.register("configure", run_configure,
                  "create configuration", requires_config=False)
registry.register("posts", run_posts, "only posts")
registry.register("medias", run_medias, "only posts with medias")
registry.register("likes", run_likes, "only likes")
registry.register("reposts", run_reposts, "only reposts")
registry.register("quotes", run_reposts, "only quotes")
registry.register("follows", run_follows, "only follows")
registry.register("bookmarks", run_follows, "only bookmarks")
registry.register("all", run_all, "target everything")
