"""Post deletion module for Skywipe"""

import time
from skywipe.auth import Auth
from skywipe.configure import Configuration


def delete_posts():
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)
    verbose = config_data.get("verbose", False)

    if verbose:
        print(
            f"Starting post deletion with batch_size={batch_size}, delay={delay}s")

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

        post_uris = [post.post.uri for post in posts]

        for uri in post_uris:
            try:
                client.delete_post(uri)
                total_deleted += 1
                if verbose:
                    print(f"Deleted post: {uri}")
            except Exception as e:
                if verbose:
                    print(f"Error deleting post {uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    print(f"Deleted {total_deleted} posts.")
