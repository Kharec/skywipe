"""Centralized logging module for Skywipe"""

import logging
import sys
from pathlib import Path


class ProgressTracker:
    def __init__(self, operation: str = "Processing"):
        self.current = 0
        self.operation = operation

    def update(self, count: int = 1):
        self.current += count

    def batch(self, batch_num: int, batch_size: int, total_batches: int | None = None):
        logger = logging.getLogger("skywipe.progress")
        if total_batches is not None:
            logger.info(
                f"{self.operation} - batch {batch_num}/{total_batches} ({batch_size} items)"
            )
        else:
            logger.info(
                f"{self.operation} - batch {batch_num} ({batch_size} items)")


class LevelFilter(logging.Filter):
    def __init__(self, min_level: int, max_level: int):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return self.min_level <= record.levelno <= self.max_level


def setup_logger(verbose: bool = False, log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger("skywipe")
    logger.propagate = False
    target_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(target_level)

    progress_logger = logging.getLogger("skywipe.progress")
    progress_logger.propagate = False

    info_handler = None
    error_handler = None
    file_handlers = []

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            file_handlers.append(handler)
        elif isinstance(handler, logging.StreamHandler):
            if handler.stream == sys.stdout:
                info_handler = handler
            elif handler.stream == sys.stderr:
                error_handler = handler

    formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    if info_handler is None:
        info_handler = logging.StreamHandler(sys.stdout)
        info_handler.addFilter(LevelFilter(logging.DEBUG, logging.INFO))
        logger.addHandler(info_handler)
    info_handler.setFormatter(formatter)
    info_handler.setLevel(target_level)

    if error_handler is None:
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.WARNING)
        logger.addHandler(error_handler)
    error_handler.setFormatter(formatter)

    for handler in file_handlers:
        handler.close()
        logger.removeHandler(handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("skywipe")


def handle_error(error: Exception, logger: logging.Logger, exit_on_error: bool = False) -> None:
    if isinstance(error, ValueError):
        logger.error(f"{error}")
    else:
        logger.error(f"Unexpected error: {error}", exc_info=True)

    if exit_on_error:
        sys.exit(1)
    else:
        raise error
