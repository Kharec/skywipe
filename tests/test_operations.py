import time

import pytest

from skywipe.operations import Operation, BookmarkStrategy


class FakeClient:
    class Me:
        did = "did:plc:fake"

    me = Me()


class FakeResponse:
    def __init__(self, items, cursor=None):
        self.items = items
        self.cursor = cursor


class FakeStrategy:
    def __init__(self, responses, fail_on=None):
        self._responses = list(responses)
        self._fail_on = fail_on

    def fetch(self, context, cursor=None):
        return self._responses.pop(0)

    def extract_items(self, response):
        return response.items

    def process_item(self, item, context):
        if self._fail_on is not None and item == self._fail_on:
            raise ValueError("boom")

    def get_cursor(self, response):
        return response.cursor


def test_operation_run_batches_filters_and_sleeps(monkeypatch):
    responses = [
        FakeResponse(items=[1, 2, 3], cursor="next"),
        FakeResponse(items=[4], cursor=None),
    ]
    operation = Operation(
        "Testing",
        strategy_type="feed",
        client=FakeClient(),
        config_data={"batch_size": 2, "delay": 1},
        filter_fn=lambda item: item != 2,
    )
    operation.strategy = FakeStrategy(responses, fail_on=3)

    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    total = operation.run()

    assert total == 2
    assert slept == [1]


def test_bookmark_strategy_extracts_uri_from_shapes():
    strategy = BookmarkStrategy()

    class Obj:
        pass

    direct = Obj()
    direct.uri = "direct"
    assert strategy._extract_bookmark_uri(direct) == "direct"

    subject = Obj()
    subject.subject = Obj()
    subject.subject.uri = "subject"
    assert strategy._extract_bookmark_uri(subject) == "subject"

    record = Obj()
    record.record = Obj()
    record.record.uri = "record"
    assert strategy._extract_bookmark_uri(record) == "record"

    post = Obj()
    post.post = Obj()
    post.post.uri = "post"
    assert strategy._extract_bookmark_uri(post) == "post"

    item = Obj()
    item.item = Obj()
    item.item.uri = "item"
    assert strategy._extract_bookmark_uri(item) == "item"

    missing = Obj()
    assert strategy._extract_bookmark_uri(missing) is None
