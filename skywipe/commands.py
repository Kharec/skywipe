"""Command implementations for Skywipe"""

from typing import Callable, Dict, Optional
from .configure import Configuration
from .operations import Operation
from .post_analysis import PostAnalyzer
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
    Operation("Deleting posts").run()


def run_medias(skip_confirmation: bool = False):
    require_confirmation("delete all posts with media", skip_confirmation)
    Operation("Deleting posts with media",
              filter_fn=lambda post: PostAnalyzer.has_media(post.post)).run()


def run_likes(skip_confirmation: bool = False):
    require_confirmation("undo all likes", skip_confirmation)
    Operation("Undoing likes", strategy_type="record",
              collection="app.bsky.feed.like").run()


def run_reposts(skip_confirmation: bool = False):
    require_confirmation("undo all reposts", skip_confirmation)
    Operation("Undoing reposts", strategy_type="record",
              collection="app.bsky.feed.repost").run()


def run_quotes(skip_confirmation: bool = False):
    require_confirmation("delete all quote posts", skip_confirmation)
    Operation("Deleting quote posts",
              filter_fn=lambda post: PostAnalyzer.has_quote(post.post)).run()


def run_follows(skip_confirmation: bool = False):
    require_confirmation("unfollow all accounts", skip_confirmation)
    Operation("Unfollowing accounts", strategy_type="record",
              collection="app.bsky.graph.follow").run()


def run_bookmarks(skip_confirmation: bool = False):
    require_confirmation("delete all bookmarks", skip_confirmation)
    Operation("Deleting bookmarks", strategy_type="bookmark").run()


def run_all(skip_confirmation: bool = False):
    logger = get_logger()

    all_commands = registry.get_all_commands()
    commands = [cmd for cmd in all_commands.keys()
                if cmd not in ("configure", "all")]

    commands_str = ", ".join(commands)
    require_confirmation(
        f"run all cleanup commands ({commands_str})", skip_confirmation)

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
