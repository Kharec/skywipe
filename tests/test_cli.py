import logging
import sys

import pytest

import skywipe.cli as cli


TEST_COMMAND = "posts"
TEST_ERROR_MESSAGE = "boom"
TEST_LOGGER_NAME = "test.cli"


def _setup_parser_mocks(monkeypatch, commands=None):
    if commands is None:
        commands = {TEST_COMMAND: "only posts"}
    monkeypatch.setattr(cli.registry, "get_all_commands", lambda: commands)


def _setup_main_mocks(monkeypatch, calls, requires_config=False, config_data=None):
    _setup_parser_mocks(monkeypatch)
    monkeypatch.setattr(cli.registry, "requires_config",
                        lambda name: requires_config)

    def mock_execute(name, skip_confirmation=False):
        calls["execute"] = (name, skip_confirmation)

    def mock_setup_logger(verbose, log_file):
        calls["setup"].append((verbose, log_file))

    def mock_require_config(logger):
        calls["require_config"].append(logger)

    monkeypatch.setattr(cli.registry, "execute", mock_execute)
    monkeypatch.setattr(cli, "setup_logger", mock_setup_logger)
    monkeypatch.setattr(cli, "require_config", mock_require_config)
    monkeypatch.setattr(cli, "get_logger",
                        lambda: logging.getLogger(TEST_LOGGER_NAME))

    if config_data is not None:
        monkeypatch.setattr(cli.Configuration, "load",
                            lambda self: config_data)


def _setup_error_mocks(monkeypatch, calls, error_factory):
    _setup_parser_mocks(monkeypatch)
    monkeypatch.setattr(cli.registry, "requires_config", lambda name: False)
    monkeypatch.setattr(cli.registry, "execute", error_factory)
    monkeypatch.setattr(cli, "setup_logger", lambda verbose, log_file: None)
    monkeypatch.setattr(cli, "get_logger",
                        lambda: logging.getLogger(TEST_LOGGER_NAME))

    def _format_error_message(error):
        if isinstance(error, KeyError):
            return error.args[0] if error.args else str(error)
        return str(error)

    def mock_handle_error(error, logger, exit_on_error=False):
        calls["handle_error"] = (type(error).__name__,
                                 _format_error_message(error), exit_on_error)

    monkeypatch.setattr(cli, "handle_error", mock_handle_error)


def test_create_parser_includes_commands(monkeypatch):
    _setup_parser_mocks(monkeypatch)
    parser = cli.create_parser()
    args = parser.parse_args([TEST_COMMAND])
    assert args.command == TEST_COMMAND


def test_create_parser_handles_multiple_commands(monkeypatch):
    commands = {
        "posts": "only posts",
        "likes": "only likes",
        "reposts": "only reposts"
    }
    _setup_parser_mocks(monkeypatch, commands)
    parser = cli.create_parser()

    args1 = parser.parse_args(["posts"])
    args2 = parser.parse_args(["likes"])
    args3 = parser.parse_args(["reposts"])

    assert args1.command == "posts"
    assert args2.command == "likes"
    assert args3.command == "reposts"


def test_create_parser_parses_yes_flag(monkeypatch):
    _setup_parser_mocks(monkeypatch)
    parser = cli.create_parser()
    args = parser.parse_args(["--yes", TEST_COMMAND])
    assert args.command == TEST_COMMAND
    assert args.yes is True


def test_create_parser_parses_without_yes_flag(monkeypatch):
    _setup_parser_mocks(monkeypatch)
    parser = cli.create_parser()
    args = parser.parse_args([TEST_COMMAND])
    assert args.command == TEST_COMMAND
    assert getattr(args, "yes", False) is False


def test_create_parser_version_flag_exits(monkeypatch):
    _setup_parser_mocks(monkeypatch)
    parser = cli.create_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--version"])
    assert excinfo.value.code == 0


def test_create_parser_requires_command(monkeypatch):
    _setup_parser_mocks(monkeypatch)
    parser = cli.create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_create_parser_rejects_invalid_command(monkeypatch):
    _setup_parser_mocks(monkeypatch)
    parser = cli.create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["invalid_command"])


def test_require_config_exits_when_missing(monkeypatch):
    monkeypatch.setattr(cli.Configuration, "exists", lambda self: False)
    logger = logging.getLogger(TEST_LOGGER_NAME)
    with pytest.raises(SystemExit) as excinfo:
        cli.require_config(logger)
    assert excinfo.value.code == 1


def test_require_config_does_not_exit_when_exists(monkeypatch):
    monkeypatch.setattr(cli.Configuration, "exists", lambda self: True)
    logger = logging.getLogger(TEST_LOGGER_NAME)
    cli.require_config(logger)


def test_main_executes_without_config(monkeypatch):
    calls = {"execute": None, "setup": [], "require_config": []}
    _setup_main_mocks(monkeypatch, calls, requires_config=False)

    monkeypatch.setattr(sys, "argv", ["skywipe", "--yes", TEST_COMMAND])
    cli.main()

    assert len(calls["require_config"]) == 0
    assert calls["setup"] == [(False, cli.LOG_FILE)]
    assert calls["execute"] == (TEST_COMMAND, True)


def test_main_loads_config_and_sets_verbose(monkeypatch):
    calls = {"setup": [], "execute": None, "require_config": []}
    _setup_main_mocks(monkeypatch, calls, requires_config=True,
                      config_data={"verbose": True})

    monkeypatch.setattr(sys, "argv", ["skywipe", TEST_COMMAND])
    cli.main()

    assert len(calls["require_config"]) == 1
    assert calls["setup"] == [(False, cli.LOG_FILE), (True, cli.LOG_FILE)]
    assert calls["execute"] == (TEST_COMMAND, False)


@pytest.mark.parametrize("config_data,expected_verbose", [
    ({}, False),
    ({"verbose": False}, False),
])
def test_main_config_verbose_defaults(monkeypatch, config_data, expected_verbose):
    calls = {"setup": [], "execute": None, "require_config": []}
    _setup_main_mocks(monkeypatch, calls, requires_config=True,
                      config_data=config_data)

    monkeypatch.setattr(sys, "argv", ["skywipe", TEST_COMMAND])
    cli.main()

    assert len(calls["require_config"]) == 1
    assert calls["setup"] == [(False, cli.LOG_FILE),
                              (expected_verbose, cli.LOG_FILE)]
    assert calls["execute"] == (TEST_COMMAND, False)


def test_main_handles_config_load_error(monkeypatch):
    calls = {"handle_error": None, "require_config": []}

    def mock_require_config(logger):
        calls["require_config"].append(logger)

    def raise_config_error(self):
        raise RuntimeError("config error")

    def _format_error_message(error):
        if isinstance(error, KeyError):
            return error.args[0] if error.args else str(error)
        return str(error)

    def mock_handle_error(error, logger, exit_on_error=False):
        calls["handle_error"] = (type(error).__name__,
                                 _format_error_message(error), exit_on_error)

    _setup_parser_mocks(monkeypatch)
    monkeypatch.setattr(cli.registry, "requires_config", lambda name: True)
    monkeypatch.setattr(cli, "require_config", mock_require_config)
    monkeypatch.setattr(cli.Configuration, "load", raise_config_error)
    monkeypatch.setattr(cli, "setup_logger", lambda verbose, log_file: None)
    monkeypatch.setattr(cli, "get_logger",
                        lambda: logging.getLogger(TEST_LOGGER_NAME))
    monkeypatch.setattr(cli, "handle_error", mock_handle_error)

    monkeypatch.setattr(sys, "argv", ["skywipe", TEST_COMMAND])
    cli.main()

    assert len(calls["require_config"]) == 1
    assert calls["handle_error"] is not None
    assert calls["handle_error"][0] == "RuntimeError"
    assert calls["handle_error"][2] is True


@pytest.mark.parametrize("error_class,error_message", [
    (ValueError, TEST_ERROR_MESSAGE),
    (RuntimeError, "runtime error"),
    (KeyError, "missing key"),
])
def test_main_handles_execute_errors(monkeypatch, error_class, error_message):
    calls = {"handle_error": None}

    def raise_error(*_args, **_kwargs):
        raise error_class(error_message)

    _setup_error_mocks(monkeypatch, calls, raise_error)
    monkeypatch.setattr(sys, "argv", ["skywipe", TEST_COMMAND])
    cli.main()

    assert calls["handle_error"] is not None
    assert calls["handle_error"][0] == error_class.__name__
    assert calls["handle_error"][1] == error_message
    assert calls["handle_error"][2] is True
