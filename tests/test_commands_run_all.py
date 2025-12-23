import logging

import pytest

import skywipe.commands as commands
import skywipe.operations as operations


def test_create_operation_handler_calls_confirmation_and_run(monkeypatch):
    calls = {"confirmed": False, "run": 0}

    def fake_confirm(message, skip_confirmation, logger):
        calls["confirmed"] = True
        assert message == "do the thing"
        assert skip_confirmation is True
        assert isinstance(logger, logging.Logger)

    class FakeOperation:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            calls["run"] += 1

    monkeypatch.setattr(commands, "require_confirmation", fake_confirm)
    monkeypatch.setattr(commands, "Operation", FakeOperation)

    handler = commands._create_operation_handler(
        "do the thing", "Test", strategy_type="feed"
    )
    handler(skip_confirmation=True)

    assert calls["confirmed"] is True
    assert calls["run"] == 1


def test_run_all_runs_in_order(monkeypatch):
    ran = []

    fake_commands = {
        "posts": "only posts",
        "likes": "only likes",
        "medias": "only medias",
        "extra": "extra",
    }
    fake_metadata = {
        "posts": {
            "operation_name": "Deleting posts",
            "strategy_type": "feed",
            "collection": None,
            "filter_fn": None,
        },
        "likes": {
            "operation_name": "Undoing likes",
            "strategy_type": "record",
            "collection": "app.bsky.feed.like",
            "filter_fn": None,
        },
        "medias": {
            "operation_name": "Deleting posts with media",
            "strategy_type": "feed",
            "collection": None,
            "filter_fn": None,
        },
        "extra": {
            "operation_name": "Extra op",
            "strategy_type": "feed",
            "collection": None,
            "filter_fn": None,
        },
    }
    fake_order = ["medias", "posts", "likes"]

    class FakeOperation:
        def __init__(self, operation_name, **kwargs):
            self.operation_name = operation_name

        def run(self):
            ran.append(self.operation_name)

    class FakeOperationContext:
        def __init__(self):
            self.client = object()
            self.config_data = {"batch_size": 1, "delay": 0}

    monkeypatch.setattr(commands, "require_confirmation",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(commands, "Operation", FakeOperation)
    monkeypatch.setattr(operations, "OperationContext", FakeOperationContext)
    monkeypatch.setattr(commands.registry,
                        "get_all_commands", lambda: fake_commands)
    monkeypatch.setattr(commands, "COMMAND_METADATA", fake_metadata)
    monkeypatch.setattr(commands, "COMMAND_EXECUTION_ORDER", fake_order)

    commands.run_all(skip_confirmation=True)

    expected = [
        "Deleting posts with media",
        "Deleting posts",
        "Undoing likes",
        "Extra op",
    ]

    assert ran == expected


def test_run_all_continues_on_error(monkeypatch):
    ran = []

    class FakeOperation:
        def __init__(self, operation_name, **kwargs):
            self.operation_name = operation_name

        def run(self):
            ran.append(self.operation_name)
            if self.operation_name == "Deleting posts":
                raise RuntimeError("fail")

    class FakeOperationContext:
        def __init__(self):
            self.client = object()
            self.config_data = {"batch_size": 1, "delay": 0}

    monkeypatch.setattr(commands, "require_confirmation",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(commands, "Operation", FakeOperation)
    monkeypatch.setattr(operations, "OperationContext", FakeOperationContext)

    commands.run_all(skip_confirmation=True)

    assert "Deleting posts" in ran
    assert len(ran) >= 2
