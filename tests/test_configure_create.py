from pathlib import Path
import yaml


def test_configuration_create_reprompts_and_writes_file(config_with_tmp_path, user_input):
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

    user_input(inputs, passwords)

    config = config_with_tmp_path
    config.create()

    assert config.config_file.exists() is True
    data = yaml.safe_load(config.config_file.read_text())
    assert data["handle"] == "alice.bsky.social"
    assert data["password"] == "longenough"
    assert data["batch_size"] == 5
    assert data["delay"] == 0
    assert data["verbose"] is False


def test_configuration_create_invalid_batch_size(config_with_tmp_path, user_input):
    inputs = iter([
        "alice.bsky.social",
        "0",
        "1",
        "y",
    ])
    passwords = iter(["longenough"])

    user_input(inputs, passwords)

    config = config_with_tmp_path
    config.create()

    assert config.config_file.exists() is False


def test_configuration_create_invalid_delay(config_with_tmp_path, user_input):
    inputs = iter([
        "alice.bsky.social",
        "10",
        "61",
        "y",
    ])
    passwords = iter(["longenough"])

    user_input(inputs, passwords)

    config = config_with_tmp_path
    config.create()

    assert config.config_file.exists() is False


def test_configuration_create_overwrite_cancel(config_with_tmp_path, user_input):
    config = config_with_tmp_path
    config.config_file.parent.mkdir(parents=True, exist_ok=True)
    config.config_file.write_text("existing")

    user_input(["n"], [])

    config.create()

    assert config.config_file.read_text() == "existing"


def test_configuration_create_write_failure(config_with_tmp_path, user_input, monkeypatch):
    user_input(
        ["alice.bsky.social", "5", "0", "y"],
        ["longenough"],
    )

    config = config_with_tmp_path

    original_open = open

    def fake_open(path, mode="r", *args, **kwargs):
        if Path(path) == config.config_file and "w" in mode:
            raise OSError("disk full")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    config.create()

    assert config.config_file.exists() is False
