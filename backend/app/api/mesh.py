from flask import Blueprint, jsonify
from app.services.registry import mesh
from app.config import Config

bp = Blueprint("mesh", __name__)


@bp.get("/<market>")
def depth(market: str):
    market = market.upper()
    if market not in Config.SUPPORTED_MARKETS:
        return jsonify({"error": f"Unsupported: {market}"}), 400
    try:
        return jsonify(mesh.depth(market))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
