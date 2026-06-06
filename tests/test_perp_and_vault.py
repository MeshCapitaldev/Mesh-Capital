import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.perp_engine import PerpEngine, PerpStatus, _positions
from app.services.compound_vault import CompoundVault, apy_from_apr, _positions as _vpos
from app.config import Config


def setup_function():
    _positions.clear()
    _vpos.clear()


def test_perp_routes_to_a_venue():
    eng = PerpEngine()
    pos = eng.open("w", "SOL-USDC", "LONG", 1000, 5.0, 150.0)
    assert pos.venue in ("drift", "zeta", "mango")
    assert pos.status == PerpStatus.OPEN


def test_perp_pnl_long_profit():
    eng = PerpEngine()
    pos = eng.open("w", "SOL-USDC", "LONG", 1000, 5.0, 150.0)
    closed = eng.close(pos.id, pos.entry_price * 1.1)
    assert closed.realized_pnl_usd > 0


def test_perp_pnl_short_profit():
    eng = PerpEngine()
    pos = eng.open("w", "SOL-USDC", "SHORT", 1000, 5.0, 150.0)
    closed = eng.close(pos.id, pos.entry_price * 0.9)
    assert closed.realized_pnl_usd > 0


def test_perp_max_leverage():
    eng = PerpEngine()
    try:
        eng.open("w", "SOL-USDC", "LONG", 1000, 999.0, 150.0)
        assert False
    except ValueError:
        pass


def test_apy_greater_than_apr():
    assert apy_from_apr(0.20, 365) > 0.20


def test_vault_deposit_and_value():
    v = CompoundVault(Config)
    pos = v.deposit("w", "jlp", 100.0)
    d = pos.to_dict(v.periods)
    assert d["deposited"] == 100.0
    assert d["apy"] > d["apr"]
    assert d["current_value"] >= 100.0


def test_vault_unknown_rejected():
    v = CompoundVault(Config)
    try:
        v.deposit("w", "nope", 100.0)
        assert False
    except ValueError:
        pass


def test_vault_list():
    v = CompoundVault(Config)
    vaults = v.list_vaults()
    assert len(vaults) >= 3
    assert all("apy" in x for x in vaults)
