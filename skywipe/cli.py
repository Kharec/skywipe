"""Main entry point for Skywipe"""

import sys
import argparse
from pathlib import Path

from .commands import registry
from .configure import Configuration
from .logger import setup_logger


def create_parser():
    commands = registry.get_all_commands()

    parser = argparse.ArgumentParser(
        description="Clean your bluesky account with style.",
        epilog="WARNING: This tool performs destructive operations. Only use it if you intend to erase data from your Bluesky account."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
        metavar="COMMAND",
        required=True
    )

    for cmd, help_text in commands.items():
        subparsers.add_parser(cmd, help=help_text)

    return parser


def require_config():
    config = Configuration()
    if not config.exists():
        logger = setup_logger(verbose=False)
        logger.error("Configuration file not found.")
        logger.error("You must run 'skywipe configure' first.")
        sys.exit(1)


def main():
    parser = create_parser()
    args = parser.parse_args()

    if registry.requires_config(args.command):
        require_config()
        config = Configuration()
        config_data = config.load()
        verbose = config_data.get("verbose", False)
        log_file = Path.home() / ".config" / "skywipe" / "skywipe.log"
        setup_logger(verbose=verbose, log_file=log_file)
    else:
        setup_logger(verbose=False)

    try:
        registry.execute(args.command)
    except ValueError as e:
        logger = setup_logger(verbose=False)
        logger.error(f"{e}")
        sys.exit(1)
    except Exception as e:
        logger = setup_logger(verbose=False)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
