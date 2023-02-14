from bottle import request
import manager
from api import APIRequest
from common import engine, abort
from settings import api_settings

app = engine.create_app()


@app.route("/", method="GET")
def get():
    settings = api_settings()
    query_fields = settings.request.query_fields
    for field in request.query:
        if field not in query_fields:
            abort.soft(code="INVALID_QUERY_FIELD", reason=f"Invalid query field: {field}")

    api_request = APIRequest.from_dict({"query": request.query})
    api_response = manager.ins().get_response(api_request)
    if not api_response:
        abort.soft(code="NO_RESPONSE", reason="No response found for the given request.")

    return api_response.to_dict()
