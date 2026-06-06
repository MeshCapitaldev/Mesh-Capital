import logging, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.ensure_ascii = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    from app.api.route import bp as route_bp
    from app.api.mesh import bp as mesh_bp
    from app.api.perp import bp as perp_bp
    from app.api.vault import bp as vault_bp

    app.register_blueprint(route_bp, url_prefix="/api")
    app.register_blueprint(mesh_bp, url_prefix="/api/mesh")
    app.register_blueprint(perp_bp, url_prefix="/api/perp")
    app.register_blueprint(vault_bp, url_prefix="/api/vault")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "mesh-capital"})

    logger.info("Mesh Capital initialized")
    return app
