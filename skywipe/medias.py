"""Media post deletion module for Skywipe"""

import time
from .auth import Auth
from .configure import Configuration


def has_media_embed(post_record):
    embed = getattr(post_record, 'embed', None)
    if not embed:
        return False

    embed_type = getattr(embed, 'py_type', None)
    media_types = {
        'app.bsky.embed.images',
        'app.bsky.embed.video',
        'app.bsky.embed.external'
    }

    if embed_type:
        embed_type_base = embed_type.split('#')[0]

        if embed_type_base in media_types:
            return True

        if embed_type_base in ('app.bsky.embed.recordWithMedia', 'app.bsky.embed.record_with_media'):
            media = getattr(embed, 'media', None)
            if media:
                media_type = getattr(media, 'py_type', None)
                if media_type:
                    media_type_base = media_type.split('#')[0]
                    if media_type_base in media_types:
                        return True

    for attr in ('images', 'video', 'external'):
        if hasattr(embed, attr):
            return True
        if isinstance(embed, dict) and embed.get(attr):
            return True
    return False


def delete_posts_with_medias():
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)
    verbose = config_data.get("verbose", False)

    if verbose:
        print(
            f"Starting media post deletion with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_deleted = 0

    while True:
        if cursor:
            response = client.get_author_feed(
                actor=did, limit=batch_size, cursor=cursor)
        else:
            response = client.get_author_feed(actor=did, limit=batch_size)

        posts = response.feed
        if not posts:
            break

        for post in posts:
            post_record = post.post

            if not has_media_embed(post_record):
                if verbose:
                    print(f"Skipping post without media: {post_record.uri}")
                continue

            try:
                client.delete_post(post_record.uri)
                total_deleted += 1
                if verbose:
                    print(f"Deleted post with media: {post_record.uri}")
            except Exception as e:
                if verbose:
                    print(f"Error deleting post {post_record.uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    print(f"Deleted {total_deleted} posts with media.")
