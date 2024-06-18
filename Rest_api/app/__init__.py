import os

from app.api import blueprint as api
from flask import Flask, current_app, send_from_directory
from flask_cors import CORS
from utils.logger import Log


def create_app(config):
    app = Flask(__name__, static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../frontend/build"))

    app.config.from_object(config)
    app.register_blueprint(api, url_prefix="/rest/1.0")
    CORS(app)

    with app.app_context():
        Log.init(
            log_level=current_app.config['LOG_LEVEL'],
            log_filepath=current_app.config['LOG_FILE']
        )

    @app.route('/<path:path>')
    @app.route('/', defaults={'path': ''})
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app
