import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.mesh import LiquidityMesh, Venue
from app.services.router import SmartRouter
from app.config import Config


def router():
    return SmartRouter(LiquidityMesh(), Config)


def test_route_structure():
    r = router().quote("SOL-USDC", "buy", 5000)
    d = r.to_dict()
    assert "blended_price" in d and "route" in d
    assert abs(sum(l["fraction"] for l in d["route"]) - 1.0) < 0.02


def test_route_splits_across_venues():
    # a large order should touch more than one venue
    r = router().quote("SOL-USDC", "buy", 40000)
    assert len(r.legs) >= 2


def test_route_beats_single_venue():
    # the blended price should be <= the best single-venue price
    r = router().quote("SOL-USDC", "buy", 40000)
    assert r.blended_price <= r.best_single_price + 1e-9
    assert r.savings_vs_best_single_pct >= 0


def test_larger_order_more_savings():
    small = router().quote("SOL-USDC", "buy", 1000)
    large = router().quote("SOL-USDC", "buy", 50000)
    # splitting matters more as size grows
    assert large.savings_vs_best_single_pct >= small.savings_vs_best_single_pct


def test_deeper_venue_gets_more():
    r = router().quote("SOL-USDC", "buy", 30000)
    # raydium is seeded deepest → should receive the largest fraction
    legs = {l.venue: l.base_amount for l in r.legs}
    assert legs.get("raydium", 0) == max(legs.values())


def test_zero_size_rejected():
    try:
        router().quote("SOL-USDC", "buy", 0)
        assert False
    except ValueError:
        pass


def test_unsupported_market():
    try:
        router().quote("FAKE-USDC", "buy", 100)
        assert False
    except ValueError:
        pass


def test_price_impact_positive_for_large_order():
    r = router().quote("SOL-USDC", "buy", 50000)
    assert r.price_impact_pct > 0
