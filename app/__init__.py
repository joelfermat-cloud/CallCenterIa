import os, logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g, jsonify
from .config import Config
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS abierto en dev
    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=False)

    # Logging con rotación + request_id
    os.makedirs('logs', exist_ok=True)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(request_id)s] %(message)s')

    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            record.request_id = getattr(g, 'request_id', '-')
            return True

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RequestIdFilter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIdFilter())

    level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'), logging.INFO)
    app.logger.setLevel(level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # Blueprints
    from .routes.core import bp as core_bp
    from .routes.api_v1 import bp as api_v1_bp
    app.register_blueprint(core_bp)
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    # Errores JSON
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        code = e.code or 500
        desc = getattr(e, 'description', str(e))
        return jsonify(error=desc, code=code, request_id=getattr(g, 'request_id', '-')), code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception('Unhandled exception')
        return jsonify(error='internal_error', code=500, request_id=getattr(g, 'request_id', '-')), 500

    return app
