from typing import Optional

import redis
from common.settings import project_settings

CLIENT = None


def get_client():
    global CLIENT

    if CLIENT:
        return CLIENT

    settings = project_settings().redis
    CLIENT = redis.StrictRedis(settings.host, settings.port, charset="utf-8", decode_responses=True)

    return CLIENT


class Counter:
    def __init__(self, name: str, redis_client: redis.Redis = None):
        self._name = name
        self._redis = redis_client or get_client()

    def incr(self) -> Optional[int]:
        try:
            res = self._redis.incr(self._name)
            return res
        except redis.exceptions.ConnectionError:
            return

    def get(self) -> Optional[int]:
        try:
            res = self._redis.get(self._name)
            return int(res) if res else 0
        except redis.exceptions.ConnectionError:
            return

    def reset(self):
        try:
            self._redis.delete(self._name)
        except redis.exceptions.ConnectionError:
            pass
