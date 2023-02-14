from __future__ import annotations
from dataclasses import dataclass, make_dataclass
from typing import List, Dict
from settings import api_settings


@dataclass
class APIResponse:
    name: str
    results: List[str]

    def to_dict(self) -> Dict:
        return {"name": self.name, "results": self.results}


def safe_make_dataclass(name: str, fields: Dict[str, any]):
    def enforce_types(self):
        for field, field_type in fields.items():
            if field_type == "string":
                setattr(self, field, str(getattr(self, field)))
            elif field_type == "int":
                setattr(self, field, int(getattr(self, field)))

    cls = make_dataclass(
        name,
        fields,
        namespace={"__post_init__": enforce_types},
    )
    return cls


Query = safe_make_dataclass("Query", api_settings().request.query_fields)


@dataclass
class APIRequest:
    query: Query

    def to_dict(self) -> dict:
        return {"query": self.query}

    @staticmethod
    def from_dict(data: dict) -> APIRequest:
        query = Query(**data.get("query"))
        return APIRequest(query=query)
