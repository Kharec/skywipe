from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from skywipe.configure import Configuration


@pytest.fixture
def config_with_tmp_path(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return Configuration()


def test_configuration_load_missing_file(config_with_tmp_path):
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        config_with_tmp_path.load()


def test_configuration_load_empty_file(config_with_tmp_path):
    config_with_tmp_path.config_file.parent.mkdir(parents=True, exist_ok=True)
    config_with_tmp_path.config_file.write_text("")

    with pytest.raises(ValueError, match="empty or invalid"):
        config_with_tmp_path.load()


def test_configuration_load_invalid_yaml(config_with_tmp_path):
    config_with_tmp_path.config_file.parent.mkdir(parents=True, exist_ok=True)
    config_with_tmp_path.config_file.write_text(": bad")

    with pytest.raises(ValueError, match="Invalid YAML"):
        config_with_tmp_path.load()


def test_configuration_load_valid_file(config_with_tmp_path):
    config_with_tmp_path.config_file.parent.mkdir(parents=True, exist_ok=True)
    config_data = {
        "handle": "alice.bsky.social",
        "password": "password123",
        "batch_size": 10,
        "delay": 1,
        "verbose": True
    }
    with open(config_with_tmp_path.config_file, "w") as f:
        yaml.dump(config_data, f)

    result = config_with_tmp_path.load()
    assert result == config_data


def test_configuration_load_file_read_error(config_with_tmp_path):
    config_with_tmp_path.config_file.parent.mkdir(parents=True, exist_ok=True)
    config_with_tmp_path.config_file.write_text("handle: alice")

    with patch("builtins.open", side_effect=IOError("Permission denied")):
        with pytest.raises(ValueError, match="Failed to read configuration file"):
            config_with_tmp_path.load()


def test_configuration_load_file_os_error(config_with_tmp_path):
    config_with_tmp_path.config_file.parent.mkdir(parents=True, exist_ok=True)
    config_with_tmp_path.config_file.write_text("handle: alice")

    with patch("builtins.open", side_effect=OSError("File is locked")):
        with pytest.raises(ValueError, match="Failed to read configuration file"):
            config_with_tmp_path.load()
