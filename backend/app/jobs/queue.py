from __future__ import annotations

from importlib.util import find_spec


class QueueDependencyError(RuntimeError):
    pass


def get_queue():
    if find_spec("redis") is None or find_spec("rq") is None:
        raise QueueDependencyError("RQ/Redis dependencies are missing; install rq and redis")
    from redis import Redis
    from rq import Queue

    connection = Redis(host="localhost", port=6379, db=0)
    return Queue("place-review", connection=connection)
