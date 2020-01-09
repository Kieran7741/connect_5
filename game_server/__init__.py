
from flask import Flask, make_response, jsonify


def create_app():
    """
    Application factory method to create app
    :return: flask.Flask
    """
    app = Flask(__name__)
    from .game import game_blueprint

    with app.app_context():
        app.register_blueprint(game_blueprint, url_prefix='/api/v1')
        @app.errorhandler(400)
        def error_handler(error):
            """Build json response message for 400 errors"""
            return make_response(jsonify({'message': error.description}), 400)

    return app
