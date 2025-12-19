"""Follow undoing module for Skywipe"""

import time
from atproto import models
from .auth import Auth
from .configure import Configuration


FOLLOW_COLLECTION = "app.bsky.graph.follow"


def unfollow_all():
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)
    verbose = config_data.get("verbose", False)

    if verbose:
        print(
            f"Starting unfollow operation with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_unfollowed = 0

    while True:
        list_params = models.ComAtprotoRepoListRecords.Params(
            repo=did,
            collection=FOLLOW_COLLECTION,
            limit=batch_size,
            cursor=cursor
        )

        response = client.com.atproto.repo.list_records(params=list_params)

        records = response.records
        if not records:
            break

        for record in records:
            try:
                record_uri = record.uri
                rkey = record_uri.rsplit("/", 1)[-1]
                delete_data = {
                    "repo": did,
                    "collection": FOLLOW_COLLECTION,
                    "rkey": rkey
                }
                client.com.atproto.repo.delete_record(data=delete_data)
                total_unfollowed += 1
                if verbose:
                    print(f"Unfollowed: {record_uri}")
            except Exception as e:
                record_uri = getattr(record, "uri", "unknown")
                if verbose:
                    print(f"Error unfollowing {record_uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    print(f"Unfollowed {total_unfollowed} accounts.")
