import logging
import sys

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


def test_progress_tracker_batch_with_total():
    tracker = ProgressTracker(operation="Testing")
    logger = logging.getLogger("skywipe.progress")
    messages = []

    class MessageHandler(logging.Handler):
        def emit(self, record):
            messages.append(self.format(record))

    handler = MessageHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    try:
        tracker.batch(1, 10, total_batches=5)
        assert messages[-1] == "Testing - batch 1/5 (10 items)"

        tracker.batch(0, 5, total_batches=0)
        assert messages[-1] == "Testing - batch 0/0 (5 items)"
    finally:
        handler.close()
        logger.removeHandler(handler)


def test_progress_tracker_batch_without_total():
    tracker = ProgressTracker(operation="Testing")
    logger = logging.getLogger("skywipe.progress")
    messages = []

    class MessageHandler(logging.Handler):
        def emit(self, record):
            messages.append(self.format(record))

    handler = MessageHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    try:
        tracker.batch(1, 10, total_batches=None)
        assert messages[-1] == "Testing - batch 1 (10 items)"
    finally:
        handler.close()
        logger.removeHandler(handler)


def test_setup_logger_does_not_duplicate_handlers():
    logger = logging.getLogger("skywipe")
    original_handlers = list(logger.handlers)
    for handler in original_handlers:
        logger.removeHandler(handler)

    try:
        setup_logger(verbose=False)
        first_handlers = list(logger.handlers)
        stream_handlers = [
            handler for handler in first_handlers
            if isinstance(handler, logging.StreamHandler)
        ]
        assert len(stream_handlers) == 2
        assert {handler.stream for handler in stream_handlers} == {
            sys.stdout,
            sys.stderr,
        }
        assert not any(
            isinstance(handler, logging.FileHandler)
            for handler in first_handlers
        )

        first_count = len(first_handlers)
        setup_logger(verbose=False)
        second_count = len(logger.handlers)
    finally:
        for handler in list(logger.handlers):
            handler.close()
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


def test_setup_logger_replaces_file_handler_when_path_changes(tmp_path):
    logger = logging.getLogger("skywipe")
    original_handlers = list(logger.handlers)
    for handler in original_handlers:
        logger.removeHandler(handler)

    log_file1 = tmp_path / "skywipe1.log"
    log_file2 = tmp_path / "skywipe2.log"
    try:
        setup_logger(verbose=False, log_file=log_file1)
        file_handlers = [
            handler for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        assert file_handlers[0].baseFilename == str(log_file1)

        setup_logger(verbose=False, log_file=log_file2)
        file_handlers = [
            handler for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        assert file_handlers[0].baseFilename == str(log_file2)
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        for handler in original_handlers:
            logger.addHandler(handler)
