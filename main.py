"""Main entry point for Skywipe"""

import sys
import argparse

from skywipe.commands import registry
from skywipe.configure import Configuration


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
        print("Error: Configuration file not found.")
        print("You must run 'skywipe configure' first.")
        sys.exit(1)


def main():
    parser = create_parser()
    args = parser.parse_args()

    if registry.requires_config(args.command):
        require_config()

    try:
        registry.execute(args.command)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
