"""Shared operation utilities and strategies for Skywipe"""

import time
from dataclasses import dataclass
from typing import Callable, Any
from atproto import models

from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


@dataclass(slots=True)
class OperationResult:
    processed: int = 0
    failed: int = 0
    skipped: int = 0


class OperationFetchError(RuntimeError):
    def __init__(
        self,
        operation_name: str,
        batch_num: int,
        error: Exception,
        result: OperationResult,
    ):
        self.operation_name = operation_name
        self.batch_num = batch_num
        self.result = result
        super().__init__(
            f"Failed to fetch items for '{operation_name}' at batch {batch_num}: {error}"
        )


class OperationContext:
    def __init__(self, client=None, config_data=None):
        self.logger = get_logger()
        self.client, self.did = self._initialize_client(client)
        self.config_data = self._initialize_config(config_data)
        self.batch_size = self.config_data.get("batch_size", 10)
        self.delay = self.config_data.get("delay", 1)

    def _initialize_client(self, client):
        if client is not None:
            did = self._extract_did(client)
            return client, did

        try:
            auth = Auth()
            client = auth.login()
            did = self._extract_did(client)
            return client, did
        except (ValueError, FileNotFoundError) as e:
            self.logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error during initialization: {e}", exc_info=True
            )
            raise ValueError(
                f"Failed to initialize operation context: {e}") from e

    def _extract_did(self, client) -> str:
        me = getattr(client, "me", None)
        did = getattr(me, "did", None)
        if not did:
            raise ValueError("Authenticated client does not expose a DID")
        return did

    def _initialize_config(self, config_data):
        if config_data is not None:
            return config_data

        try:
            config = Configuration()
            return config.load()
        except (ValueError, FileNotFoundError) as e:
            self.logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error loading configuration: {e}", exc_info=True
            )
            raise ValueError(f"Failed to load configuration: {e}") from e


class BaseStrategy:
    def fetch(self, context: OperationContext, cursor: str | None = None) -> Any:
        raise NotImplementedError

    def extract_items(self, response: Any) -> list[Any]:
        raise NotImplementedError

    def process_item(self, item: Any, context: OperationContext) -> None:
        raise NotImplementedError

    def get_cursor(self, response: Any) -> str | None:
        return response.cursor


class RecordDeletionStrategy(BaseStrategy):
    def __init__(self, collection: str):
        self.collection = collection

    def fetch(self, context: OperationContext, cursor: str | None = None) -> Any:
        list_params = models.ComAtprotoRepoListRecords.Params(
            repo=context.did,
            collection=self.collection,
            limit=context.batch_size,
            cursor=cursor,
        )
        return context.client.com.atproto.repo.list_records(params=list_params)

    def extract_items(self, response: Any) -> list[Any]:
        return response.records

    def process_item(self, item: Any, context: OperationContext) -> None:
        record_uri = item.uri
        rkey = record_uri.rsplit("/", 1)[-1]
        delete_data = models.ComAtprotoRepoDeleteRecord.Data(
            repo=context.did,
            collection=self.collection,
            rkey=rkey,
        )
        context.client.com.atproto.repo.delete_record(data=delete_data)
        context.logger.debug(f"Deleted: {record_uri}")


class FeedStrategy(BaseStrategy):
    def fetch(self, context: OperationContext, cursor: str | None = None) -> Any:
        if cursor:
            return context.client.get_author_feed(
                actor=context.did, limit=context.batch_size, cursor=cursor
            )
        return context.client.get_author_feed(
            actor=context.did, limit=context.batch_size
        )

    def extract_items(self, response: Any) -> list[Any]:
        return response.feed

    def process_item(self, item: Any, context: OperationContext) -> None:
        uri = item.post.uri
        context.client.delete_post(uri)
        context.logger.debug(f"Deleted post: {uri}")


class BookmarkStrategy(BaseStrategy):
    def fetch(self, context: OperationContext, cursor: str | None = None) -> Any:
        get_params = models.AppBskyBookmarkGetBookmarks.Params(
            limit=context.batch_size, cursor=cursor
        )
        return context.client.app.bsky.bookmark.get_bookmarks(params=get_params)

    def extract_items(self, response: Any) -> list[Any]:
        return response.bookmarks

    def process_item(self, item: Any, context: OperationContext) -> None:
        bookmark_uri = self._extract_bookmark_uri(item)
        if not bookmark_uri:
            raise ValueError("Unable to find bookmark URI")

        delete_data = models.AppBskyBookmarkDeleteBookmark.Data(
            uri=bookmark_uri)
        context.client.app.bsky.bookmark.delete_bookmark(data=delete_data)
        context.logger.debug(f"Deleted bookmark: {bookmark_uri}")

    def _extract_bookmark_uri(self, bookmark: Any) -> str | None:
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
        collection: str | None = None,
        filter_fn: Callable[[Any], bool] | None = None,
        client=None,
        config_data=None,
    ):
        self.operation_name = operation_name
        self.filter_fn = filter_fn
        self._client = client
        self._config_data = config_data
        self.strategy: BaseStrategy

        if strategy_type == "record":
            if not collection:
                raise ValueError("Collection is required for record strategy")
            self.strategy = RecordDeletionStrategy(collection)
        elif strategy_type == "bookmark":
            self.strategy = BookmarkStrategy()
        else:
            self.strategy = FeedStrategy()

    def run(self) -> OperationResult:
        context = OperationContext(
            client=self._client, config_data=self._config_data)
        progress = ProgressTracker(operation=self.operation_name)

        context.logger.info(
            f"Starting {self.operation_name} with batch_size={context.batch_size}, delay={context.delay}s"
        )

        cursor = None
        result = OperationResult()
        batch_num = 0

        while True:
            batch_num += 1
            try:
                response = self.strategy.fetch(context, cursor)
                items = self.strategy.extract_items(response)
            except Exception as e:
                raise OperationFetchError(
                    self.operation_name,
                    batch_num,
                    e,
                    OperationResult(
                        processed=result.processed,
                        failed=result.failed,
                        skipped=result.skipped,
                    ),
                ) from e

            if not items:
                break

            progress.batch(batch_num, len(items))

            for item in items:
                if self.filter_fn and not self.filter_fn(item):
                    result.skipped += 1
                    continue

                try:
                    self.strategy.process_item(item, context)
                    result.processed += 1
                    progress.update(1)
                except Exception as e:
                    result.failed += 1
                    context.logger.error(f"Error processing item: {e}")

            cursor = self.strategy.get_cursor(response)
            if not cursor:
                break

            if context.delay > 0:
                time.sleep(context.delay)

        context.logger.info(
            f"{self.operation_name}: processed={result.processed}, failed={result.failed}, skipped={result.skipped}."
        )
        return result
