import pytest

from skywipe.commands import CommandRegistry


def test_command_registry_register_and_execute():
    registry = CommandRegistry()
    calls = {"configure": 0, "run": 0, "skip": None}

    def configure_handler():
        calls["configure"] += 1

    def run_handler(skip_confirmation=False):
        calls["run"] += 1
        calls["skip"] = skip_confirmation

    registry.register("configure", configure_handler,
                      "config", requires_config=False)
    registry.register("run", run_handler, "run")

    registry.execute("configure")
    registry.execute("run", skip_confirmation=True)

    assert calls["configure"] == 1
    assert calls["run"] == 1
    assert calls["skip"] is True


def test_command_registry_unknown_command():
    registry = CommandRegistry()
    with pytest.raises(ValueError, match="Unknown command"):
        registry.execute("nope")
