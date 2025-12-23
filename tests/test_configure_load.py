from pathlib import Path

import pytest

from skywipe.configure import Configuration


def test_configuration_load_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Configuration()
    with pytest.raises(FileNotFoundError):
        config.load()


def test_configuration_load_empty_file(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Configuration()
    config.config_file.parent.mkdir(parents=True, exist_ok=True)
    config.config_file.write_text("")

    with pytest.raises(ValueError, match="empty or invalid"):
        config.load()


def test_configuration_load_invalid_yaml(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config = Configuration()
    config.config_file.parent.mkdir(parents=True, exist_ok=True)
    config.config_file.write_text(": bad")

    with pytest.raises(ValueError, match="Invalid YAML"):
        config.load()
