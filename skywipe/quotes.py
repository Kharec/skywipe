"""Quote post deletion module for Skywipe"""

import time
from .auth import Auth
from .configure import Configuration


def has_quote_embed(post_record):
    embed = getattr(post_record, 'embed', None)
    if not embed:
        return False

    embed_type = getattr(embed, 'py_type', None)
    if embed_type:
        embed_type_base = embed_type.split('#')[0]
        quote_types = {
            'app.bsky.embed.record',
            'app.bsky.embed.recordWithMedia',
            'app.bsky.embed.record_with_media'
        }
        if embed_type_base in quote_types:
            return True

    if hasattr(embed, 'record') or (isinstance(embed, dict) and embed.get('record')):
        return True

    return False


def delete_quotes():
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)
    verbose = config_data.get("verbose", False)

    if verbose:
        print(
            f"Starting quote post deletion with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_deleted = 0

    while True:
        response = client.get_author_feed(
            actor=did, limit=batch_size, cursor=cursor)

        posts = response.feed
        if not posts:
            break

        for post in posts:
            post_record = post.post

            if not has_quote_embed(post_record):
                if verbose:
                    print(f"Skipping post without quote: {post_record.uri}")
                continue

            try:
                client.delete_post(post_record.uri)
                total_deleted += 1
                if verbose:
                    print(f"Deleted quote post: {post_record.uri}")
            except Exception as e:
                if verbose:
                    print(f"Error deleting quote post {post_record.uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    print(f"Deleted {total_deleted} quote posts.")
