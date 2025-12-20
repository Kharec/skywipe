"""Safeguard module for Skywipe"""

import sys
from .logger import get_logger


CONFIRM_RESPONSES = {"yes", "y"}


def require_confirmation(operation: str, skip_confirmation: bool = False) -> None:
    if skip_confirmation:
        return

    logger = get_logger()
    logger.warning(f"This will {operation}")
    logger.warning("This operation is DESTRUCTIVE and cannot be undone!")

    try:
        response = input(
            "Are you sure you want to continue? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        logger.info("\nOperation cancelled.")
        sys.exit(0)

    if response not in CONFIRM_RESPONSES:
        logger.info("Operation cancelled.")
        sys.exit(0)
