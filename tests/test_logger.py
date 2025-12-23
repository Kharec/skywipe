import logging

from skywipe.logger import LevelFilter, ProgressTracker, setup_logger


def test_level_filter_accepts_in_range():
    logger = logging.getLogger("test.level_filter")
    record = logger.makeRecord(
        name="test.level_filter",
        level=logging.INFO,
        fn="test",
        lno=1,
        msg="message",
        args=(),
        exc_info=None,
    )
    level_filter = LevelFilter(logging.DEBUG, logging.INFO)
    assert level_filter.filter(record) is True


def test_level_filter_rejects_out_of_range():
    logger = logging.getLogger("test.level_filter")
    record = logger.makeRecord(
        name="test.level_filter",
        level=logging.ERROR,
        fn="test",
        lno=1,
        msg="message",
        args=(),
        exc_info=None,
    )
    level_filter = LevelFilter(logging.DEBUG, logging.INFO)
    assert level_filter.filter(record) is False


def test_progress_tracker_updates_counts():
    tracker = ProgressTracker(operation="Testing")
    tracker.update()
    tracker.update(2)
    assert tracker.current == 3


def test_setup_logger_does_not_duplicate_handlers():
    logger = logging.getLogger("skywipe")
    original_handlers = list(logger.handlers)
    for handler in original_handlers:
        logger.removeHandler(handler)

    try:
        setup_logger(verbose=False)
        first_count = len(logger.handlers)
        setup_logger(verbose=False)
        second_count = len(logger.handlers)
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        for handler in original_handlers:
            logger.addHandler(handler)

    assert first_count == second_count


def test_setup_logger_file_handler_lifecycle(tmp_path):
    logger = logging.getLogger("skywipe")
    original_handlers = list(logger.handlers)
    for handler in original_handlers:
        logger.removeHandler(handler)

    log_file = tmp_path / "skywipe.log"
    try:
        setup_logger(verbose=False, log_file=log_file)
        file_handlers = [
            handler for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        assert file_handlers[0].baseFilename == str(log_file)

        setup_logger(verbose=False, log_file=None)
        file_handlers = [
            handler for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        ]
        assert file_handlers == []
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        for handler in original_handlers:
            logger.addHandler(handler)
