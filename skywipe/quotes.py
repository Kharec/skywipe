"""Quote post deletion module for Skywipe"""

import time
from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


def delete_quotes_posts():
    logger = get_logger()
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)

    logger.info(f"Starting quote post deletion with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_deleted = 0
    batch_num = 0
    progress = ProgressTracker(operation="Deleting quote posts")

    while True:
        batch_num += 1
        response = client.get_author_feed(
            actor=did, limit=batch_size, cursor=cursor)

        posts = response.feed
        if not posts:
            break

        progress.batch(batch_num, len(posts))

        for post in posts:
            post_record = post.post

            embed = getattr(post_record, 'embed', None)
            has_quote = False
            if embed:
                embed_type = getattr(embed, 'py_type', None)
                if embed_type:
                    embed_type_base = embed_type.split('#')[0]
                    quote_types = {
                        'app.bsky.embed.record',
                        'app.bsky.embed.recordWithMedia',
                        'app.bsky.embed.record_with_media'
                    }
                    if embed_type_base in quote_types:
                        has_quote = True
                
                if not has_quote and (hasattr(embed, 'record') or (isinstance(embed, dict) and embed.get('record'))):
                    has_quote = True

            if not has_quote:
                logger.debug(f"Skipping post without quote: {post_record.uri}")
                continue

            try:
                client.delete_post(post_record.uri)
                total_deleted += 1
                progress.update(1)
                logger.debug(f"Deleted quote post: {post_record.uri}")
            except Exception as e:
                logger.error(f"Error deleting quote post {post_record.uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    logger.info(f"Deleted {total_deleted} quote posts.")
