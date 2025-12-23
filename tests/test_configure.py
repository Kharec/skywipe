import pytest

from skywipe.configure import _validate_handle, _validate_password


@pytest.mark.parametrize(
    "handle,expected_valid",
    [
        ("", False),
        ("a" * 254, False),
        ("has space", False),
        ("invalid_handle!", False),
        ("alice", True),
        ("alice.bsky.social", True),
        ("did:plc:abcd1234", True),
    ],
)
def test_validate_handle(handle, expected_valid):
    result = _validate_handle(handle)
    assert result.is_valid is expected_valid


@pytest.mark.parametrize(
    "password,expected_valid",
    [
        ("", False),
        ("short", False),
        ("longenough", True),
    ],
)
def test_validate_password(password, expected_valid):
    result = _validate_password(password)
    assert result.is_valid is expected_valid
