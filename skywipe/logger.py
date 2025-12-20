"""Centralized logging module for Skywipe"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ProgressTracker:
    def __init__(self, operation: str = "Processing"):
        self.current = 0
        self.operation = operation

    def update(self, count: int = 1):
        self.current += count

    def batch(self, batch_num: int, batch_size: int, total_batches: Optional[int] = None):
        logger = logging.getLogger("skywipe.progress")
        if total_batches:
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


def setup_logger(verbose: bool = False, log_file: Optional[Path] = None) -> logging.Logger:
    logger = logging.getLogger("skywipe")
    target_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(target_level)

    info_handler = None
    error_handler = None
    file_handlers = []

    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            if handler.stream == sys.stdout:
                info_handler = handler
            elif handler.stream == sys.stderr:
                error_handler = handler
        elif isinstance(handler, logging.FileHandler):
            file_handlers.append(handler)

    formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    if info_handler is None:
        info_handler = logging.StreamHandler(sys.stdout)
        info_handler.addFilter(LevelFilter(logging.DEBUG, logging.INFO))
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)
    info_handler.setLevel(target_level)

    if error_handler is None:
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    if log_file:
        if not file_handlers:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
    else:
        for handler in file_handlers:
            handler.close()
            logger.removeHandler(handler)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("skywipe")
