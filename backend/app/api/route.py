from flask import Blueprint, jsonify, request
from app.services.registry import router
from app.config import Config
from app.utils.logger import get_logger

bp = Blueprint("route", __name__)
logger = get_logger(__name__)


@bp.post("/route/quote")
def route_quote():
    body = request.get_json(silent=True) or {}
    market = body.get("market", "SOL-USDC").upper()
    side = body.get("side", "buy")
    size = body.get("size")
    if size is None:
        return jsonify({"error": "size required"}), 400
    if market not in Config.SUPPORTED_MARKETS:
        return jsonify({"error": f"Unsupported market: {market}"}), 400
    try:
        result = router.quote(market, side, float(size))
        return jsonify(result.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Route error: {e}")
        return jsonify({"error": str(e)}), 500
