from types import SimpleNamespace

from skywipe.operations import (
    RecordDeletionStrategy,
    FeedStrategy,
    BookmarkStrategy,
)


def test_record_deletion_strategy_fetch_and_process(monkeypatch):
    captured = {}

    class FakeParams:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    def fake_list_records(params):
        captured["params"] = params
        return "response"

    def fake_delete_record(data):
        captured["delete"] = data

    client = SimpleNamespace(
        com=SimpleNamespace(
            atproto=SimpleNamespace(
                repo=SimpleNamespace(
                    list_records=fake_list_records,
                    delete_record=fake_delete_record,
                )
            )
        )
    )
    context = SimpleNamespace(
        did="did:plc:fake",
        batch_size=2,
        client=client,
        logger=SimpleNamespace(debug=lambda *_args, **_kwargs: None),
    )

    monkeypatch.setattr(
        "skywipe.operations.models.ComAtprotoRepoListRecords.Params",
        FakeParams,
    )

    strategy = RecordDeletionStrategy("app.bsky.feed.like")
    response = strategy.fetch(context, cursor="next")
    assert response == "response"
    assert captured["params"].kwargs == {
        "repo": "did:plc:fake",
        "collection": "app.bsky.feed.like",
        "limit": 2,
        "cursor": "next",
    }

    record = SimpleNamespace(uri="at://did:plc:fake/app.bsky.feed.like/abc123")
    strategy.process_item(record, context)
    assert captured["delete"].repo == "did:plc:fake"
    assert captured["delete"].collection == "app.bsky.feed.like"
    assert captured["delete"].rkey == "abc123"


def test_feed_strategy_fetch_and_process():
    captured = {}

    def fake_get_author_feed(**kwargs):
        captured["feed"] = kwargs
        return "feed"

    def fake_delete_post(uri):
        captured["delete"] = uri

    client = SimpleNamespace(
        get_author_feed=fake_get_author_feed,
        delete_post=fake_delete_post,
    )
    context = SimpleNamespace(
        did="did:plc:fake",
        batch_size=3,
        client=client,
        logger=SimpleNamespace(debug=lambda *_args, **_kwargs: None),
    )

    strategy = FeedStrategy()
    response = strategy.fetch(context, cursor=None)
    assert response == "feed"
    assert captured["feed"] == {"actor": "did:plc:fake", "limit": 3}

    response = strategy.fetch(context, cursor="next")
    assert response == "feed"
    assert captured["feed"] == {
        "actor": "did:plc:fake", "limit": 3, "cursor": "next"}

    post = SimpleNamespace(post=SimpleNamespace(uri="at://post"))
    strategy.process_item(post, context)
    assert captured["delete"] == "at://post"


def test_bookmark_strategy_fetch(monkeypatch):
    captured = {}

    class FakeParams:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    def fake_get_bookmarks(params):
        captured["params"] = params
        return "bookmarks"

    client = SimpleNamespace(
        app=SimpleNamespace(
            bsky=SimpleNamespace(
                bookmark=SimpleNamespace(get_bookmarks=fake_get_bookmarks)
            )
        )
    )
    context = SimpleNamespace(batch_size=5, client=client)

    monkeypatch.setattr(
        "skywipe.operations.models.AppBskyBookmarkGetBookmarks.Params",
        FakeParams,
    )

    strategy = BookmarkStrategy()
    response = strategy.fetch(context, cursor="cursor")
    assert response == "bookmarks"
    assert captured["params"].kwargs == {"limit": 5, "cursor": "cursor"}
