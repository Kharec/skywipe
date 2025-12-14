"""Command implementations for Skywipe CLI."""

from typing import Callable, Dict, Optional
from skywipe.configure import Configuration


CommandHandler = Callable[[], None]


class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, CommandHandler] = {}
        self._help_texts: Dict[str, str] = {}
        self._requires_config: Dict[str, bool] = {}

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


_registry = CommandRegistry()


def get_registry() -> CommandRegistry:
    return _registry


def run_configure():
    config = Configuration()
    config.create()


def run_posts():
    print("Command 'posts' is not yet implemented.")


def run_medias():
    print("Command 'medias' is not yet implemented.")


def run_likes():
    print("Command 'likes' is not yet implemented.")


def run_reposts():
    print("Command 'reposts' is not yet implemented.")


def run_follows():
    print("Command 'follows' is not yet implemented.")


def run_all():
    registry = get_registry()
    registry.execute("posts")
    registry.execute("medias")
    registry.execute("likes")
    registry.execute("reposts")
    registry.execute("follows")


_registry.register("configure", run_configure,
                   "create configuration", requires_config=False)
_registry.register("posts", run_posts, "only posts")
_registry.register("medias", run_medias, "only posts with medias")
_registry.register("likes", run_likes, "only likes")
_registry.register("reposts", run_reposts, "only reposts")
_registry.register("follows", run_follows, "only follows")
_registry.register("all", run_all, "target everything")
