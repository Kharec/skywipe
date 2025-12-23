"""Command implementations for Skywipe"""

from typing import Callable, Any
from .configure import Configuration
from .operations import Operation
from .post_analysis import PostAnalyzer
from .logger import get_logger, handle_error
from .safeguard import require_confirmation


CommandHandler = Callable[..., None]


COMMAND_METADATA = {
    "posts": {
        "confirmation": "delete all posts",
        "help_text": "only posts",
        "operation_name": "Deleting posts",
        "strategy_type": "feed",
        "collection": None,
        "filter_fn": None,
    },
    "medias": {
        "confirmation": "delete all posts with media",
        "help_text": "only posts with medias",
        "operation_name": "Deleting posts with media",
        "strategy_type": "feed",
        "collection": None,
        "filter_fn": lambda post: PostAnalyzer.has_media(post.post),
    },
    "likes": {
        "confirmation": "undo all likes",
        "help_text": "only likes",
        "operation_name": "Undoing likes",
        "strategy_type": "record",
        "collection": "app.bsky.feed.like",
        "filter_fn": None,
    },
    "reposts": {
        "confirmation": "undo all reposts",
        "help_text": "only reposts",
        "operation_name": "Undoing reposts",
        "strategy_type": "record",
        "collection": "app.bsky.feed.repost",
        "filter_fn": None,
    },
    "quotes": {
        "confirmation": "delete all quote posts",
        "help_text": "only quotes",
        "operation_name": "Deleting quote posts",
        "strategy_type": "feed",
        "collection": None,
        "filter_fn": lambda post: PostAnalyzer.has_quote(post.post),
    },
    "follows": {
        "confirmation": "unfollow all accounts",
        "help_text": "only follows",
        "operation_name": "Unfollowing accounts",
        "strategy_type": "record",
        "collection": "app.bsky.graph.follow",
        "filter_fn": None,
    },
    "bookmarks": {
        "confirmation": "delete all bookmarks",
        "help_text": "only bookmarks",
        "operation_name": "Deleting bookmarks",
        "strategy_type": "bookmark",
        "collection": None,
        "filter_fn": None,
    },
}

COMMAND_EXECUTION_ORDER = [
    "quotes",
    "medias",
    "posts",
    "likes",
    "reposts",
    "follows",
    "bookmarks",
]


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

    def get_handler(self, name: str) -> CommandHandler | None:
        return self._commands.get(name)

    def get_help_text(self, name: str) -> str | None:
        return self._help_texts.get(name)

    def requires_config(self, name: str) -> bool:
        return self._requires_config.get(name, True)

    def get_all_commands(self) -> dict[str, str]:
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
    collection: str | None = None,
    filter_fn: Callable[[Any], bool] | None = None
) -> CommandHandler:
    logger = get_logger()

    def handler(skip_confirmation: bool = False):
        require_confirmation(confirmation_message, skip_confirmation, logger)
        try:
            Operation(
                operation_name,
                strategy_type=strategy_type,
                collection=collection,
                filter_fn=filter_fn
            ).run()
        except (ValueError, Exception) as e:
            handle_error(e, logger)
    return handler


def run_configure():
    config = Configuration()
    config.create()


def _create_command_handlers():
    handlers = {}
    for cmd, metadata in COMMAND_METADATA.items():
        handlers[cmd] = _create_operation_handler(
            metadata["confirmation"],
            metadata["operation_name"],
            strategy_type=metadata["strategy_type"],
            collection=metadata["collection"],
            filter_fn=metadata["filter_fn"]
        )
    return handlers


_command_handlers = _create_command_handlers()


def run_all(skip_confirmation: bool = False):
    logger = get_logger()

    all_commands = registry.get_all_commands()
    available_commands = [cmd for cmd in all_commands.keys()
                          if cmd not in ("configure", "all")]

    commands = [cmd for cmd in COMMAND_EXECUTION_ORDER
                if cmd in available_commands]

    commands.extend([cmd for cmd in available_commands
                     if cmd not in COMMAND_EXECUTION_ORDER])

    commands_str = ", ".join(commands)
    all_confirmation = f"run all cleanup commands ({commands_str})"
    require_confirmation(all_confirmation, skip_confirmation, logger)

    logger.info("Running all cleanup commands...")

    from .operations import OperationContext
    try:
        context = OperationContext()
        shared_client = context.client
        shared_config_data = context.config_data
    except Exception as e:
        logger.error(
            f"Failed to initialize shared context: {e}", exc_info=True)
        raise

    for cmd in commands:
        try:
            logger.info(f"Starting command: {cmd}")
            metadata = COMMAND_METADATA.get(cmd)
            if metadata:
                Operation(
                    metadata["operation_name"],
                    strategy_type=metadata["strategy_type"],
                    collection=metadata["collection"],
                    filter_fn=metadata["filter_fn"],
                    client=shared_client,
                    config_data=shared_config_data
                ).run()
            else:
                registry.execute(cmd, skip_confirmation=True)
            logger.info(f"Completed command: {cmd}")
        except Exception as e:
            logger.error(f"Error running '{cmd}': {e}", exc_info=True)
            continue
    logger.info("All commands completed.")


registry.register("configure", run_configure,
                  "create configuration", requires_config=False)
for cmd, metadata in COMMAND_METADATA.items():
    registry.register(cmd, _command_handlers[cmd], metadata["help_text"])
registry.register("all", run_all, "target everything")
