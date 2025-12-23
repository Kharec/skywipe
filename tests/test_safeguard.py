import logging

import pytest

from skywipe.safeguard import require_confirmation


def test_require_confirmation_skips_prompt():
    logger = logging.getLogger("test.safeguard")
    require_confirmation("do nothing", skip_confirmation=True, logger=logger)


def test_require_confirmation_accepts_yes(monkeypatch):
    logger = logging.getLogger("test.safeguard")
    monkeypatch.setattr("builtins.input", lambda _: "y")
    require_confirmation("do nothing", logger=logger)


def test_require_confirmation_rejects_no(monkeypatch):
    logger = logging.getLogger("test.safeguard")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    with pytest.raises(SystemExit) as excinfo:
        require_confirmation("do nothing", logger=logger)
    assert excinfo.value.code == 0


def test_require_confirmation_handles_eof(monkeypatch):
    logger = logging.getLogger("test.safeguard")

    def raise_eof(_prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    with pytest.raises(SystemExit) as excinfo:
        require_confirmation("do nothing", logger=logger)
    assert excinfo.value.code == 0
