import logging
import random
from typing import List, Optional, Dict
from mockredis import MockRedis
from api import APIResponse, APIRequest
from common.redis_client import get_client, Counter

import redis
from settings import api_settings, Response

INSTANCE = None


class Manager:
    REDIS_PREFIX = "response_count_"

    def __init__(
        self,
        responses: List[Response] = None,
        redis_client: redis.Redis | MockRedis = None,
        track: bool = None,
    ):
        self._responses: List[Response] = responses or api_settings().responses
        self._redis: redis.Redis = redis_client or get_client()
        self._track = track or api_settings().settings.track_to_redis

    @property
    def stats(self) -> Dict[str, int]:
        stats = {}
        for response in self._responses:
            name = response.name
            counter = Counter(self.REDIS_PREFIX + response.name, self._redis)
            stats[name] = counter.get()

        return stats

    def track(self, req: APIResponse) -> None:
        if not self._track:
            return

        counter = Counter(self.REDIS_PREFIX + req.name, self._redis)
        res = counter.incr()
        if not res:
            logging.error(f"Could not track response: {req.name}")
            return

        logging.error(f"Tracking response: {req.name} - {res}")

    def get_response(self, request: APIRequest) -> Optional[APIResponse]:
        responses: List[APIResponse] = []
        for response in self._responses:
            match = eval(response.expression, request.to_dict())
            if match:
                res = []
                for action in response.actions:
                    res.append(action.do(request.to_dict()))

                name = response.name
                responses.append(APIResponse(name, res))

        if not responses:
            return

        if len(responses) == 1:
            res = responses[0]
        else:
            res = random.choice(responses)

        self.track(res)
        return res


def ins() -> Manager:
    global INSTANCE
    if not INSTANCE:
        INSTANCE = Manager()
    return INSTANCE
