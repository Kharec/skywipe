"""Shared operation utilities and strategies for Skywipe"""

import time
from typing import Callable, Optional, Any
from atproto import models

from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


class OperationContext:
    def __init__(self):
        self.logger = get_logger()
        self.auth = Auth()
        self.client = self.auth.login()
        self.config = Configuration()
        self.config_data = self.config.load()
        self.batch_size = self.config_data.get("batch_size", 10)
        self.delay = self.config_data.get("delay", 1)
        self.did = self.client.me.did


class RecordDeletionStrategy:
    def __init__(self, collection: str):
        self.collection = collection

    def fetch(self, context: OperationContext, cursor: Optional[str] = None):
        list_params = models.ComAtprotoRepoListRecords.Params(
            repo=context.did,
            collection=self.collection,
            limit=context.batch_size,
            cursor=cursor
        )
        return context.client.com.atproto.repo.list_records(params=list_params)

    def extract_items(self, response):
        return response.records

    def get_cursor(self, response):
        return response.cursor

    def process_item(self, record, context: OperationContext):
        record_uri = record.uri
        rkey = record_uri.rsplit("/", 1)[-1]
        delete_data = {
            "repo": context.did,
            "collection": self.collection,
            "rkey": rkey
        }
        context.client.com.atproto.repo.delete_record(data=delete_data)
        context.logger.debug(f"Deleted: {record_uri}")


class FeedStrategy:
    def fetch(self, context: OperationContext, cursor: Optional[str] = None):
        if cursor:
            return context.client.get_author_feed(
                actor=context.did, limit=context.batch_size, cursor=cursor
            )
        return context.client.get_author_feed(actor=context.did, limit=context.batch_size)

    def extract_items(self, response):
        return response.feed

    def get_cursor(self, response):
        return response.cursor

    def process_item(self, post, context: OperationContext):
        uri = post.post.uri
        context.client.delete_post(uri)
        context.logger.debug(f"Deleted post: {uri}")


class BookmarkStrategy:
    def fetch(self, context: OperationContext, cursor: Optional[str] = None):
        get_params = models.AppBskyBookmarkGetBookmarks.Params(
            limit=context.batch_size,
            cursor=cursor
        )
        return context.client.app.bsky.bookmark.get_bookmarks(params=get_params)

    def extract_items(self, response):
        return response.bookmarks

    def get_cursor(self, response):
        return response.cursor

    def process_item(self, bookmark, context: OperationContext):
        bookmark_uri = self._extract_bookmark_uri(bookmark)
        if not bookmark_uri:
            raise ValueError("Unable to find bookmark URI")

        delete_data = models.AppBskyBookmarkDeleteBookmark.Data(
            uri=bookmark_uri)
        context.client.app.bsky.bookmark.delete_bookmark(data=delete_data)
        context.logger.debug(f"Deleted bookmark: {bookmark_uri}")

    def _extract_bookmark_uri(self, bookmark):
        if hasattr(bookmark, "uri"):
            return bookmark.uri

        for attr_name in ("subject", "record", "post", "item"):
            if hasattr(bookmark, attr_name):
                nested = getattr(bookmark, attr_name)
                if hasattr(nested, "uri"):
                    return nested.uri
        return None


class Operation:
    def __init__(
        self,
        operation_name: str,
        strategy_type: str = "feed",
        collection: Optional[str] = None,
        filter_fn: Optional[Callable[[Any], bool]] = None
    ):
        self.operation_name = operation_name
        self.filter_fn = filter_fn

        if strategy_type == "record":
            if not collection:
                raise ValueError("Collection is required for record strategy")
            self.strategy = RecordDeletionStrategy(collection)
        elif strategy_type == "bookmark":
            self.strategy = BookmarkStrategy()
        else:
            self.strategy = FeedStrategy()

    def run(self) -> int:
        context = OperationContext()
        progress = ProgressTracker(operation=self.operation_name)

        context.logger.info(
            f"Starting {self.operation_name} with batch_size={context.batch_size}, delay={context.delay}s"
        )

        cursor = None
        total_processed = 0
        batch_num = 0

        while True:
            batch_num += 1
            response = self.strategy.fetch(context, cursor)
            items = self.strategy.extract_items(response)

            if not items:
                break

            progress.batch(batch_num, len(items))

            for item in items:
                if self.filter_fn and not self.filter_fn(item):
                    continue

                try:
                    self.strategy.process_item(item, context)
                    total_processed += 1
                    progress.update(1)
                except Exception as e:
                    context.logger.error(f"Error processing item: {e}")

            cursor = self.strategy.get_cursor(response)
            if not cursor:
                break

            if context.delay > 0:
                time.sleep(context.delay)

        context.logger.info(
            f"{self.operation_name}: {total_processed} items processed.")
        return total_processed
