from pathlib import Path

import yaml

from skywipe.configure import Configuration


def test_configuration_create_reprompts_and_writes_file(monkeypatch, tmp_path, user_input):
    inputs = iter([
        "bad handle",
        "alice.bsky.social",
        "5",
        "0",
        "n",
    ])
    passwords = iter([
        "short",
        "longenough",
    ])

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    user_input(inputs, passwords)

    config = Configuration()
    config.create()

    assert config.config_file.exists() is True
    data = yaml.safe_load(config.config_file.read_text())
    assert data["handle"] == "alice.bsky.social"
    assert data["password"] == "longenough"
    assert data["batch_size"] == 5
    assert data["delay"] == 0
    assert data["verbose"] is False


def test_configuration_create_invalid_batch_size(monkeypatch, tmp_path, user_input):
    inputs = iter([
        "alice.bsky.social",
        "0",
        "1",
        "y",
    ])
    passwords = iter(["longenough"])

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    user_input(inputs, passwords)

    config = Configuration()
    config.create()

    assert config.config_file.exists() is False


def test_configuration_create_invalid_delay(monkeypatch, tmp_path, user_input):
    inputs = iter([
        "alice.bsky.social",
        "10",
        "61",
        "y",
    ])
    passwords = iter(["longenough"])

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    user_input(inputs, passwords)

    config = Configuration()
    config.create()

    assert config.config_file.exists() is False


def test_configuration_create_overwrite_cancel(monkeypatch, tmp_path, user_input):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Configuration()
    config.config_file.parent.mkdir(parents=True, exist_ok=True)
    config.config_file.write_text("existing")

    user_input(["n"], [])

    config.create()

    assert config.config_file.read_text() == "existing"


def test_configuration_create_write_failure(monkeypatch, tmp_path, user_input):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    user_input(
        ["alice.bsky.social", "5", "0", "y"],
        ["longenough"],
    )

    config = Configuration()

    original_open = open

    def fake_open(path, mode="r", *args, **kwargs):
        if Path(path) == config.config_file and "w" in mode:
            raise OSError("disk full")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    config.create()

    assert config.config_file.exists() is False
