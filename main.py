"""Main entry point for Skywipe"""

import sys
import argparse

from skywipe.commands import *


def main():
    parser = argparse.ArgumentParser(
        description="Clean your bluesky account with style")
    parser.add_argument(
        "command",
        choices=["all", "configure", "posts",
                 "medias", "likes", "reposts", "follows"],
        help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "configure":
        run_configure()
    

if __name__ == '__main__':
    main()
