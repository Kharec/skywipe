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
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    info_handler.addFilter(LevelFilter(logging.DEBUG, logging.INFO))
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

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
