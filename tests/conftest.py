from typing import Iterable, Callable

import pytest


@pytest.fixture
def user_input(monkeypatch) -> Callable[[Iterable[str], Iterable[str]], None]:
    def _set(inputs: Iterable[str], passwords: Iterable[str]) -> None:
        input_iter = iter(inputs)
        password_iter = iter(passwords)

        monkeypatch.setattr("builtins.input", lambda _prompt: next(input_iter))
        monkeypatch.setattr("getpass.getpass",
                            lambda _prompt: next(password_iter))

    return _set
