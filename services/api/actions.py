from __future__ import annotations
import logging
from enum import Enum
from typing import Dict, Optional, Type
from abc import ABC, abstractmethod

import requests


class ActionType(Enum):
    URL = "url"
    EVAL = "eval"


class Action(ABC):
    @abstractmethod
    def __init__(self, action_type: ActionType, params: Optional[Dict] = None):
        self.action_type = action_type
        self.params = params

    def do(self, request: Dict):
        raise NotImplementedError

    def to_dict(self):
        return {"type": self.action_type.value, **self.params}

    @staticmethod
    @abstractmethod
    def from_dict(data: Dict):
        raise NotImplementedError


class Url(Action):
    def __init__(self, params: Optional[Dict] = None):
        super().__init__(action_type=ActionType.URL, params=params)

    def do(self, request: Dict):
        try:
            url = self.params.get("url")
            field = self.params.get("field")
            method = self.params.get("method", "GET")

            if method == "POST":
                res = requests.post(url)
            else:
                res = requests.get(url)

            val = res.json().get(field, "")
            return val
        except Exception as e:
            logging.error(e)
            return None

    @staticmethod
    def from_dict(data: Dict) -> Url:
        return Url(params=data)


class Eval(Action):
    def do(self, request: Dict):
        try:
            expression = self.params.get("expression")
            val = eval(expression, request)
            return val
        except Exception as e:
            logging.error(e)
            return None

    def __init__(self, params: Optional[Dict] = None):
        super().__init__(action_type=ActionType.EVAL, params=params)

    @staticmethod
    def from_dict(data: Dict) -> Eval:
        return Eval(params=data)


ACTIONS: Dict[str, Type[Action]] = {"url": Url, "eval": Eval}
