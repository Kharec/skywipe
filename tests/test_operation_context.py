import pytest

import skywipe.operations as operations


def test_operation_context_raises_on_auth_error(monkeypatch):
    class FakeAuth:
        def login(self):
            raise ValueError("bad auth")

    monkeypatch.setattr(operations, "Auth", FakeAuth)

    with pytest.raises(ValueError, match="bad auth"):
        operations.OperationContext()


def test_operation_context_raises_on_config_error(monkeypatch):
    class FakeClient:
        class Me:
            did = "did:plc:fake"

        me = Me()

    def fake_load(self):
        raise ValueError("bad config")

    monkeypatch.setattr(operations.Configuration, "load", fake_load)

    with pytest.raises(ValueError, match="bad config"):
        operations.OperationContext(client=FakeClient())
