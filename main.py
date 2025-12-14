"""Main entry point for Skywipe"""

import sys
import argparse

from skywipe.commands import run_configure
from skywipe.configuration import Configuration


COMMANDS = {
    "all": "target everything",
    "configure": "create configuration",
    "posts": "only posts",
    "medias": "only posts with medias",
    "likes": "only likes",
    "reposts": "only reposts",
    "follows": "only follows",
}


def _create_parser():
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

    for cmd, help_text in COMMANDS.items():
        subparsers.add_parser(cmd, help=help_text)

    return parser


def _check_config_required(command: str) -> bool:
    return command != "configure"


def _require_config():
    config = Configuration()
    if not config.exists():
        print("Error: Configuration file not found.")
        print("You must run 'skywipe configure' first.")
        sys.exit(1)


def main():
    parser = _create_parser()
    args = parser.parse_args()

    if _check_config_required(args.command):
        _require_config()

    if args.command == "configure":
        run_configure()
    else:
        print(f"Command '{args.command}' is not yet implemented.")


if __name__ == '__main__':
    main()
