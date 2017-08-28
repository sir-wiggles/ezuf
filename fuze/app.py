from flask import Response, jsonify
from fuze import views
from functools import wraps


class JsonResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(JsonResponse, cls).force_type(rv, environ)


def get_http_exception_handler(app):
    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        exc = handle_http_exception(exception)
        return jsonify({
            'code': exc.code,
            'message': exc.description
        }), exc.code

    return ret_val


def configure(app, db):
    app.response_class = JsonResponse

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    app.handle_http_exception = get_http_exception_handler(app)

    # Health check
    app.add_url_rule(
        "/health", view_func=views.health, methods=["GET"]
    )

    # User related routes
    app.add_url_rule(
        "/user", view_func=views.user_create, methods=["POST"]
    )
    app.add_url_rule(
        "/user", view_func=views.user_delete, methods=["DELETE"]
    )

    # Meeting related routes
    app.add_url_rule(
        "/meeting", view_func=views.meeting_create, methods=["POST"]
    )
    app.add_url_rule(
        "/meeting", view_func=views.meeting_delete, methods=["DELETE"]
    )
    app.add_url_rule(
        "/meeting", view_func=views.meeting_share, methods=["PUT"]
    )
    app.add_url_rule(
        "/meeting", view_func=views.meeting_get, methods=["GET"]
    )

    app.add_url_rule(
        "/view", view_func=views.meeting_view, methods=["GET"]
    )

    app.add_url_rule(
        "/recording", view_func=views.recording_visibility, methods=["PUT"]
    )

    app.add_url_rule(
        "/download/<string:recording_id>",
        view_func=views.download,
        methods=["GET"]
    )

    return app
