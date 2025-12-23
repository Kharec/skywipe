import logging
import sys

import pytest

import skywipe.cli as cli


def test_create_parser_includes_commands(monkeypatch):
    monkeypatch.setattr(cli.registry, "get_all_commands",
                        lambda: {"posts": "only posts"})
    parser = cli.create_parser()
    args = parser.parse_args(["posts"])
    assert args.command == "posts"


def test_require_config_exits_when_missing(monkeypatch):
    monkeypatch.setattr(cli.Configuration, "exists", lambda self: False)
    logger = logging.getLogger("test.cli")
    with pytest.raises(SystemExit) as excinfo:
        cli.require_config(logger)
    assert excinfo.value.code == 1


def test_main_executes_without_config(monkeypatch):
    calls = {"execute": None, "setup": []}

    monkeypatch.setattr(cli.registry, "get_all_commands",
                        lambda: {"posts": "only posts"})
    monkeypatch.setattr(cli.registry, "requires_config", lambda name: False)
    monkeypatch.setattr(cli.registry, "execute", lambda name, skip_confirmation=False: calls.update(
        {"execute": (name, skip_confirmation)}
    ))
    monkeypatch.setattr(cli, "setup_logger", lambda verbose,
                        log_file: calls["setup"].append((verbose, log_file)))
    monkeypatch.setattr(cli, "get_logger",
                        lambda: logging.getLogger("test.cli"))

    monkeypatch.setattr(sys, "argv", ["skywipe", "--yes", "posts"])
    cli.main()

    assert calls["setup"] == [(False, cli.LOG_FILE)]
    assert calls["execute"] == ("posts", True)


def test_main_loads_config_and_sets_verbose(monkeypatch):
    calls = {"setup": [], "execute": None, "require_config": 0}

    monkeypatch.setattr(cli.registry, "get_all_commands",
                        lambda: {"posts": "only posts"})
    monkeypatch.setattr(cli.registry, "requires_config", lambda name: True)
    monkeypatch.setattr(cli.registry, "execute", lambda name, skip_confirmation=False: calls.update(
        {"execute": (name, skip_confirmation)}
    ))
    monkeypatch.setattr(cli, "require_config", lambda logger: calls.update(
        {"require_config": calls["require_config"] + 1}
    ))
    monkeypatch.setattr(cli.Configuration, "load",
                        lambda self: {"verbose": True})
    monkeypatch.setattr(cli, "setup_logger", lambda verbose,
                        log_file: calls["setup"].append((verbose, log_file)))
    monkeypatch.setattr(cli, "get_logger",
                        lambda: logging.getLogger("test.cli"))

    monkeypatch.setattr(sys, "argv", ["skywipe", "posts"])
    cli.main()

    assert calls["require_config"] == 1
    assert calls["setup"] == [(False, cli.LOG_FILE), (True, cli.LOG_FILE)]
    assert calls["execute"] == ("posts", False)


def test_main_handles_execute_error(monkeypatch):
    calls = {"handle_error": None}

    monkeypatch.setattr(cli.registry, "get_all_commands",
                        lambda: {"posts": "only posts"})
    monkeypatch.setattr(cli.registry, "requires_config", lambda name: False)

    def raise_error(*_args, **_kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(cli.registry, "execute", raise_error)
    monkeypatch.setattr(cli, "setup_logger", lambda verbose, log_file: None)
    monkeypatch.setattr(cli, "get_logger",
                        lambda: logging.getLogger("test.cli"))

    def fake_handle_error(error, logger, exit_on_error=False):
        calls["handle_error"] = (str(error), exit_on_error)

    monkeypatch.setattr(cli, "handle_error", fake_handle_error)
    monkeypatch.setattr(sys, "argv", ["skywipe", "posts"])

    cli.main()

    assert calls["handle_error"] == ("boom", True)
