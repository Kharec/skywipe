"""Bookmark deletion module for Skywipe"""

import time
from atproto import models
from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


def delete_bookmarks():
    logger = get_logger()
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)

    logger.info(
        f"Starting bookmark deletion with batch_size={batch_size}, delay={delay}s")

    cursor = None
    total_deleted = 0
    batch_num = 0
    progress = ProgressTracker(operation="Deleting bookmarks")

    while True:
        batch_num += 1
        get_params = models.AppBskyBookmarkGetBookmarks.Params(
            limit=batch_size,
            cursor=cursor
        )

        response = client.app.bsky.bookmark.get_bookmarks(params=get_params)

        bookmarks = response.bookmarks
        if not bookmarks:
            break

        progress.batch(batch_num, len(bookmarks))

        for bookmark in bookmarks:
            try:
                bookmark_uri = None
                if hasattr(bookmark, "uri"):
                    bookmark_uri = bookmark.uri
                else:
                    for attr_name in ("subject", "record", "post", "item"):
                        if hasattr(bookmark, attr_name):
                            nested = getattr(bookmark, attr_name)
                            if hasattr(nested, "uri"):
                                bookmark_uri = nested.uri
                                break

                if not bookmark_uri:
                    logger.debug("Skipping bookmark: unable to find uri")
                    continue

                delete_data = models.AppBskyBookmarkDeleteBookmark.Data(
                    uri=bookmark_uri
                )
                client.app.bsky.bookmark.delete_bookmark(data=delete_data)
                total_deleted += 1
                progress.update(1)
                logger.debug(f"Deleted bookmark: {bookmark_uri}")
            except Exception as e:
                bookmark_uri = getattr(bookmark, "uri", "unknown")
                logger.error(f"Error deleting bookmark {bookmark_uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    logger.info(f"Deleted {total_deleted} bookmarks.")
