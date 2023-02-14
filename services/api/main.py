import logging

from common import utils, engine
from common.settings import project_settings
from routes.route import app as route_app

app = engine.create_app()


app.mount("/api", route_app)

if __name__ == "__main__":
    settings = project_settings().api
    port = settings.port
    utils.initialize_logging_to_stdout()

    from wsgiref.simple_server import make_server, WSGIServer
    from socketserver import ThreadingMixIn

    class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
        daemon_threads = True

    class Server:
        def __init__(self, wsgi_app, listen="0.0.0.0", app_port=port):
            self.wsgi_app = wsgi_app
            self.listen = listen
            self.port = app_port
            self.server = make_server(self.listen, self.port, self.wsgi_app, ThreadingWSGIServer)

        def serve_forever(self):
            self.server.serve_forever()

    logging.info(f"Serving on port: {port}")
    httpd = Server(app, app_port=port)
    httpd.serve_forever()
