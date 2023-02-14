from dataclasses import dataclass
from typing import List

from api import Request
from manager import Manager
from mockredis import MockRedis

from responses import Response


@dataclass
class TestCase:
    responses: List[Response]
    should_match: bool
    redis: MockRedis = MockRedis()
    return_value: str = ""

    def check(self, request: Request):
        manager = Manager(self.responses, redis_client=self.redis)
        res = manager.get_response(request)
        assert bool(res) == self.should_match
        if self.should_match:
            assert res.name == self.return_value


def test_basic_manager_get():
    request = Request.from_dict({"query": {"name": "valid", "birth_year": 1999}})

    cases = [
        # non valid case
        TestCase(
            responses=[Response(name="non_valid", expression="1 != 1", actions=[])],
            should_match=False,
        ),
        # 1/1 valid case
        TestCase(
            responses=[Response(name="valid", expression="1 == 1", actions=[])],
            should_match=True,
            return_value="valid",
        ),
        # 1/2 valid case
        TestCase(
            responses=[
                Response(name="valid", expression="1 == 1", actions=[]),
                Response(name="non_valid", expression="1 != 1", actions=[]),
            ],
            should_match=True,
            return_value="valid",
        ),
        # 2/2 valid case
        TestCase(
            responses=[
                Response(name="valid", expression="1 == 1", actions=[]),
                Response(name="valid", expression="1 == 1", actions=[]),
            ],
            should_match=True,
            return_value="valid",
        ),
    ]

    for test in cases:
        test.check(request)


def test_basic_stats():
    request = Request.from_dict({"query": {"name": "valid", "birth_year": 1999}})
    redis_client = MockRedis()
    responses = [Response(name="valid", expression="1 == 1", actions=[])]
    manager = Manager(responses=responses, redis_client=redis_client)
    for _ in range(10):
        manager.get_response(request)

    assert manager.stats.get("valid") == 10
