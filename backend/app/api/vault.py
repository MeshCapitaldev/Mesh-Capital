from flask import Blueprint, jsonify, request
from app.services.registry import vaults

bp = Blueprint("vault", __name__)


@bp.get("")
def list_vaults():
    return jsonify({"vaults": vaults.list_vaults()})


@bp.post("/deposit")
def deposit():
    body = request.get_json(silent=True) or {}
    for f in ["wallet", "vault", "amount"]:
        if f not in body:
            return jsonify({"error": f"Missing: {f}"}), 400
    try:
        pos = vaults.deposit(body["wallet"], body["vault"], float(body["amount"]))
        return jsonify(pos.to_dict(vaults.periods)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.get("/positions/<wallet>")
def positions(wallet: str):
    return jsonify({"positions": vaults.list_for_wallet(wallet)})
