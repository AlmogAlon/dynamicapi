from __future__ import annotations

import logging
from typing import Dict, List
import glob
import json
import os
from dataclasses import dataclass

import redis
from mockredis import MockRedis

from actions import ACTIONS, Action
from common.redis_client import get_client


@dataclass
class Response:
    name: str
    expression: str
    actions: List[Action]

    @staticmethod
    def from_path(path: str) -> Response:
        with open(path, "r") as f:
            data = json.load(f)
        name = data.get("name")
        match = data.get("expression")
        actions = []
        for json_action in data.get("actions", []):
            action_type = json_action.get("type")
            if action_type not in ACTIONS:
                raise Exception("Not Implemented! (bug)")

            action = ACTIONS[action_type].from_dict(json_action)
            actions.append(action)
        return Response(name=name, expression=match, actions=actions)

    def to_dict(self):
        return {
            "name": self.name,
            "expression": self.expression,
            "actions": [action.to_dict() for action in self.actions],
        }

    @staticmethod
    def from_dict(data: dict):
        actions = []
        for action in data.get("actions"):
            action_type = action.get("type")
            if action_type not in ACTIONS:
                continue
            try:
                action_ins = ACTIONS[action_type].from_dict(action)
            except Exception as e:
                continue
            actions.append(action_ins)

        return Response(
            name=data.get("name"),
            expression=data.get("expression"),
            actions=actions,
        )


@dataclass
class Rules:
    responses: List[Response]
    request: Request

    def to_dict(self):
        return {
            "responses": [response.to_dict() for response in self.responses],
            "request": self.request.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict):
        return Rules(
            responses=[Response.from_dict(response) for response in data.get("responses", [])],
            request=Request.from_dict(data.get("request", {})),
        )


@dataclass
class ManageConfig:
    key: str = "rules"
    redis_client: redis.Redis | MockRedis = get_client()

    def get(self):
        try:
            data = self.redis_client.get(self.key)
        except redis.exceptions.ConnectionError:
            data = None

        if not data:
            res = get_rules()
            self.deploy(res)
            return res

        return Rules.from_dict(json.loads(data))

    def deploy(self, rules: Rules):
        try:
            self.redis_client.set(self.key, json.dumps(rules.to_dict()))
        except Exception as e:
            logging.error(f"Failed to deploy rules: {e}")


def get_rules() -> Rules:
    responses_dir = "config/responses"
    res = []
    for json_file in glob.glob(os.path.join(responses_dir, "*.json")):
        try:
            res.append(Response.from_path(json_file))
        except Exception as e:
            continue
    request_file = "config/request/settings.json"
    request = Request.from_path(request_file)
    return Rules(responses=res, request=request)


@dataclass
class Request(object):
    query_fields: Dict[str, any]

    @staticmethod
    def from_path(path: str) -> Request:
        with open(path, "r") as f:
            data = json.load(f)

        return Request(query_fields=data.get("query", {}).get("fields", {}))

    def to_dict(self):
        return {
            "query_fields": self.query_fields,
        }

    @staticmethod
    def from_dict(data: dict):
        return Request(
            query_fields=data.get("query_fields", []),
        )


@dataclass
class Settings:
    track_to_redis: bool = True

    @staticmethod
    def from_path(path: str) -> Settings:
        with open(path, "r") as f:
            data = json.load(f)
        return Settings(**data)


def get_settings() -> Settings:
    settings_file = "config/settings.json"
    return Settings.from_path(settings_file)


@dataclass
class API(object):
    responses: List[Response]
    request: Request
    settings: Settings


def api_settings(project: str = None) -> API:
    if project is None:
        project = _DEFAULT_PROJECT

    settings = _api_settings.get(project)
    if settings is None:
        settings = _api_settings.get(_DEFAULT_PROJECT)

    return settings


_DEFAULT_PROJECT = "dynamic_api"

_api_settings: Dict[str, API] = {
    _DEFAULT_PROJECT: API(
        responses=ManageConfig().get().responses,
        request=ManageConfig().get().request,
        settings=get_settings(),
    )
}
