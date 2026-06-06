from flask import Blueprint, jsonify, request
from app.services.registry import perps, solana
from app.config import Config
from app.utils.logger import get_logger

bp = Blueprint("perp", __name__)
logger = get_logger(__name__)


@bp.post("/open")
def open_perp():
    body = request.get_json(silent=True) or {}
    for f in ["market", "side", "size_usd", "leverage"]:
        if f not in body:
            return jsonify({"error": f"Missing: {f}"}), 400
    market = body["market"].upper()
    if market not in Config.SUPPORTED_MARKETS:
        return jsonify({"error": f"Unsupported market: {market}"}), 400
    try:
        price = solana.get_price_usd(market) or 0.0
        pos = perps.open(body.get("wallet", ""), market, body["side"],
                         float(body["size_usd"]), float(body["leverage"]), price)
        return jsonify(pos.to_dict(current_price=price)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Perp open error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/<position_id>/close")
def close_perp(position_id: str):
    pos = perps.get(position_id)
    if not pos:
        return jsonify({"error": "Position not found"}), 404
    price = solana.get_price_usd(pos.market) or pos.entry_price
    closed = perps.close(position_id, price)
    return jsonify(closed.to_dict())


@bp.get("")
def list_perps():
    wallet = request.args.get("wallet")
    if not wallet:
        return jsonify({"error": "wallet required"}), 400
    out = []
    for p in perps.list_for_wallet(wallet):
        price = solana.get_price_usd(p.market) if p.status.value == "open" else None
        out.append(p.to_dict(current_price=price))
    return jsonify({"positions": out, "total": len(out)})
