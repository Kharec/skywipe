"""Command implementations for Skywipe"""

from typing import Callable, Dict, Optional
from .configure import Configuration
from .posts import delete_all_posts
from .medias import delete_posts_with_medias
from .likes import undo_likes
from .reposts import undo_reposts
from .quotes import delete_quotes_posts
from .follows import unfollow_all
from .bookmarks import delete_bookmarks
from .logger import get_logger
from .safeguard import require_confirmation


CommandHandler = Callable[..., None]


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

    def execute(self, name: str, skip_confirmation: bool = False):
        handler = self.get_handler(name)
        if handler:
            if name == "configure":
                handler()
            else:
                handler(skip_confirmation)
        else:
            raise ValueError(f"Unknown command: {name}")


registry = CommandRegistry()


def run_configure():
    config = Configuration()
    config.create()


def run_posts(skip_confirmation: bool = False):
    require_confirmation("delete all posts", skip_confirmation)
    delete_all_posts()


def run_medias(skip_confirmation: bool = False):
    require_confirmation("delete all posts with media", skip_confirmation)
    delete_posts_with_medias()


def run_likes(skip_confirmation: bool = False):
    require_confirmation("undo all likes", skip_confirmation)
    undo_likes()


def run_reposts(skip_confirmation: bool = False):
    require_confirmation("undo all reposts", skip_confirmation)
    undo_reposts()


def run_quotes(skip_confirmation: bool = False):
    require_confirmation("delete all quote posts", skip_confirmation)
    delete_quotes_posts()


def run_follows(skip_confirmation: bool = False):
    require_confirmation("unfollow all accounts", skip_confirmation)
    unfollow_all()


def run_bookmarks(skip_confirmation: bool = False):
    require_confirmation("delete all bookmarks", skip_confirmation)
    delete_bookmarks()


def run_all(skip_confirmation: bool = False):
    logger = get_logger()
    require_confirmation(
        "run all cleanup commands (posts, likes, reposts, follows, bookmarks)", skip_confirmation)

    commands = ["posts", "likes", "reposts", "follows", "bookmarks"]

    logger.info("Running all cleanup commands...")
    for cmd in commands:
        try:
            logger.info(f"Starting command: {cmd}")
            registry.execute(cmd, skip_confirmation=True)
            logger.info(f"Completed command: {cmd}")
        except Exception as e:
            logger.error(f"Error running '{cmd}': {e}", exc_info=True)
            continue
    logger.info("All commands completed.")


registry.register("configure", run_configure,
                  "create configuration", requires_config=False)
registry.register("posts", run_posts, "only posts")
registry.register("medias", run_medias, "only posts with medias")
registry.register("likes", run_likes, "only likes")
registry.register("reposts", run_reposts, "only reposts")
registry.register("quotes", run_quotes, "only quotes")
registry.register("follows", run_follows, "only follows")
registry.register("bookmarks", run_bookmarks, "only bookmarks")
registry.register("all", run_all, "target everything")
