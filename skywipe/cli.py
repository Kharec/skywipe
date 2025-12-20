"""Main entry point for Skywipe"""

import sys
import argparse
from pathlib import Path

from .commands import registry
from .configure import Configuration
from .logger import setup_logger, get_logger, handle_error


LOG_FILE = Path.home() / ".cache" / "skywipe" / "skywipe.log"


def create_parser():
    commands = registry.get_all_commands()

    parser = argparse.ArgumentParser(
        description="Clean your bluesky account with style.",
        epilog="WARNING: This tool deletes your Bluesky data permanently."
    )

    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt and proceed with destructive operations"
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


def require_config(logger):
    config = Configuration()
    if not config.exists():
        logger.error("Configuration file not found.")
        logger.error("You must run 'skywipe configure' first.")
        sys.exit(1)


def main():
    parser = create_parser()
    args = parser.parse_args()

    setup_logger(verbose=False, log_file=LOG_FILE)
    logger = get_logger()

    if registry.requires_config(args.command):
        require_config(logger)
        config = Configuration()
        config_data = config.load()
        verbose = config_data.get("verbose", False)
        setup_logger(verbose=verbose, log_file=LOG_FILE)

    try:
        registry.execute(
            args.command, skip_confirmation=getattr(args, "yes", False))
    except (ValueError, Exception) as e:
        handle_error(e, logger, exit_on_error=True)


if __name__ == '__main__':
    main()
