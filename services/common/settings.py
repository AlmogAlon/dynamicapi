import os
from dataclasses import dataclass
from typing import Dict

from dotenv import load_dotenv

load_dotenv()


@dataclass
class API(object):
    host: str = os.getenv("API_HOST")
    port: int = int(os.getenv("API_PORT"))


@dataclass
class Redis(object):
    host: str = os.getenv("REDIS_HOST")
    port: int = os.getenv("REDIS_PORT")


@dataclass
class Settings:
    redis: Redis = Redis()
    api: API = API()


_DEFAULT_PROJECT = "dynamic_api"

_project_settings: Dict[str, Settings] = {_DEFAULT_PROJECT: Settings()}


def project_settings(project: str = None) -> Settings:
    if project is None:
        project = _DEFAULT_PROJECT

    settings = _project_settings.get(project)
    if settings is None:
        settings = _project_settings.get(_DEFAULT_PROJECT)

    return settings
