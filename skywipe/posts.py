"""Post deletion module for Skywipe"""

import time
from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


def delete_all_posts():
    logger = get_logger()
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)

    logger.info(
        f"Starting post deletion with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_deleted = 0
    batch_num = 0
    progress = ProgressTracker(operation="Deleting posts")

    while True:
        batch_num += 1
        if cursor:
            response = client.get_author_feed(
                actor=did, limit=batch_size, cursor=cursor)
        else:
            response = client.get_author_feed(actor=did, limit=batch_size)

        posts = response.feed
        if not posts:
            break

        post_uris = [post.post.uri for post in posts]
        progress.batch(batch_num, len(post_uris))

        for uri in post_uris:
            try:
                client.delete_post(uri)
                total_deleted += 1
                progress.update(1)
                logger.debug(f"Deleted post: {uri}")
            except Exception as e:
                logger.error(f"Error deleting post {uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    logger.info(f"Deleted {total_deleted} posts.")
