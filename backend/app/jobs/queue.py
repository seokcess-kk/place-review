from __future__ import annotations

from importlib.util import find_spec


class QueueDependencyError(RuntimeError):
    pass


def get_redis_connection():
    if find_spec("redis") is None:
        raise QueueDependencyError("Redis is missing; install redis")
    from redis import Redis
    return Redis(host="localhost", port=6379, db=0)


def get_queue():
    if find_spec("redis") is None or find_spec("rq") is None:
        raise QueueDependencyError("RQ/Redis dependencies are missing; install rq and redis")
    from rq import Queue

    connection = get_redis_connection()
    return Queue(connection=connection)
