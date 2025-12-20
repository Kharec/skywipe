"""Command implementations for Skywipe"""

from typing import Callable, Dict, Optional, Any
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


def _create_operation_handler(
    confirmation_message: str,
    operation_name: str,
    strategy_type: str = "feed",
    collection: Optional[str] = None,
    filter_fn: Optional[Callable[[Any], bool]] = None
) -> CommandHandler:
    def handler(skip_confirmation: bool = False):
        require_confirmation(confirmation_message, skip_confirmation)
        Operation(
            operation_name,
            strategy_type=strategy_type,
            collection=collection,
            filter_fn=filter_fn
        ).run()
    return handler


def run_configure():
    config = Configuration()
    config.create()


run_posts = _create_operation_handler(
    "delete all posts",
    "Deleting posts"
)

run_medias = _create_operation_handler(
    "delete all posts with media",
    "Deleting posts with media",
    filter_fn=lambda post: PostAnalyzer.has_media(post.post)
)

run_likes = _create_operation_handler(
    "undo all likes",
    "Undoing likes",
    strategy_type="record",
    collection="app.bsky.feed.like"
)

run_reposts = _create_operation_handler(
    "undo all reposts",
    "Undoing reposts",
    strategy_type="record",
    collection="app.bsky.feed.repost"
)

run_quotes = _create_operation_handler(
    "delete all quote posts",
    "Deleting quote posts",
    filter_fn=lambda post: PostAnalyzer.has_quote(post.post)
)

run_follows = _create_operation_handler(
    "unfollow all accounts",
    "Unfollowing accounts",
    strategy_type="record",
    collection="app.bsky.graph.follow"
)

run_bookmarks = _create_operation_handler(
    "delete all bookmarks",
    "Deleting bookmarks",
    strategy_type="bookmark"
)


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
