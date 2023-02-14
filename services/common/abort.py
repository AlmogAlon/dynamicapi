import json as _json
from typing import Dict
from bottle import HTTPResponse, response


def json(status: int = 500, body: Dict = None):
    resp = HTTPResponse(
        body=_json.dumps(body),
        status=status,
        headers={"content-type": "application/json"},
        **response.headers,
    )
    raise resp


def soft(code: str, reason: str, source: str = None, *, fields=None, status=400):
    json(
        body={
            "code": code,
            "reason": reason,
            "source": source,
            "fields": fields,
        },
        status=status,
    )
