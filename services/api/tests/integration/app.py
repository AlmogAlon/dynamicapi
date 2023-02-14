import webtest.app
from routes.route import app as route_app


def init():
    app = webtest.TestApp(route_app)
    return app
