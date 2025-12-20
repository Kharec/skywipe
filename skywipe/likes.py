"""Like undoing module for Skywipe"""

import time
from atproto import models
from .auth import Auth
from .configure import Configuration
from .logger import get_logger, ProgressTracker


LIKE_COLLECTION = "app.bsky.feed.like"


def undo_likes():
    logger = get_logger()
    auth = Auth()
    client = auth.login()
    config = Configuration()
    config_data = config.load()

    batch_size = config_data.get("batch_size", 10)
    delay = config_data.get("delay", 1)

    logger.info(
        f"Starting like deletion with batch_size={batch_size}, delay={delay}s")

    did = client.me.did
    cursor = None
    total_undone = 0
    batch_num = 0
    progress = ProgressTracker(operation="Undoing likes")

    while True:
        batch_num += 1
        list_params = models.ComAtprotoRepoListRecords.Params(
            repo=did,
            collection=LIKE_COLLECTION,
            limit=batch_size,
            cursor=cursor
        )

        response = client.com.atproto.repo.list_records(params=list_params)

        records = response.records
        if not records:
            break

        progress.batch(batch_num, len(records))

        for record in records:
            try:
                record_uri = record.uri
                rkey = record_uri.rsplit("/", 1)[-1]
                delete_data = {
                    "repo": did,
                    "collection": LIKE_COLLECTION,
                    "rkey": rkey
                }
                client.com.atproto.repo.delete_record(data=delete_data)
                total_undone += 1
                progress.update(1)
                logger.debug(f"Undone like: {record_uri}")
            except Exception as e:
                record_uri = getattr(record, "uri", "unknown")
                logger.error(f"Error undoing like {record_uri}: {e}")

        cursor = response.cursor
        if not cursor:
            break

        if delay > 0:
            time.sleep(delay)

    logger.info(f"Undone {total_undone} likes.")
