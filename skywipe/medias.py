"""Media post deletion module for Skywipe"""

import time
from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


def delete_posts_with_medias():
    logger = get_logger()
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)

    logger.info(
        f"Starting media post deletion with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_deleted = 0
    batch_num = 0
    progress = ProgressTracker(operation="Deleting posts with media")

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
            has_media = False
            if embed:
                embed_type = getattr(embed, 'py_type', None)
                media_types = {
                    'app.bsky.embed.images',
                    'app.bsky.embed.video',
                    'app.bsky.embed.external'
                }

                if embed_type:
                    embed_type_base = embed_type.split('#')[0]

                    if embed_type_base in media_types:
                        has_media = True

                    if not has_media and embed_type_base in ('app.bsky.embed.recordWithMedia', 'app.bsky.embed.record_with_media'):
                        media = getattr(embed, 'media', None)
                        if media:
                            media_type = getattr(media, 'py_type', None)
                            if media_type:
                                media_type_base = media_type.split('#')[0]
                                if media_type_base in media_types:
                                    has_media = True

                if not has_media:
                    for attr in ('images', 'video', 'external'):
                        if hasattr(embed, attr):
                            has_media = True
                            break
                        if isinstance(embed, dict) and embed.get(attr):
                            has_media = True
                            break

            if not has_media:
                logger.debug(f"Skipping post without media: {post_record.uri}")
                continue

            try:
                client.delete_post(post_record.uri)
                total_deleted += 1
                progress.update(1)
                logger.debug(f"Deleted post with media: {post_record.uri}")
            except Exception as e:
                logger.error(f"Error deleting post {post_record.uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    logger.info(f"Deleted {total_deleted} posts with media.")
