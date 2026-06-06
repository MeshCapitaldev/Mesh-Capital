import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.mesh import LiquidityMesh, Venue


def test_venues_returned():
    m = LiquidityMesh()
    vs = m.venues("SOL-USDC")
    assert len(vs) >= 2
    assert all(isinstance(v, Venue) for v in vs)


def test_venues_are_copies():
    m = LiquidityMesh()
    a = m.venues("SOL-USDC")
    a[0].base_reserve = 1  # mutate the copy
    b = m.venues("SOL-USDC")
    assert b[0].base_reserve != 1  # live mesh untouched


def test_depth_summary():
    m = LiquidityMesh()
    d = m.depth("SOL-USDC")
    assert d["venue_count"] >= 2
    assert d["total_depth_quote"] > 0


def test_venue_buy_cost_increases_with_size():
    v = Venue("x", 1000, 150000)
    small = v.quote_buy_cost(10)
    large = v.quote_buy_cost(100)
    assert large > small * 9  # convex impact


def test_marginal_price_rises_as_filled():
    v = Venue("x", 1000, 150000)
    early = v.marginal_buy_price(0)
    late = v.marginal_buy_price(500)
    assert late > early


def test_unsupported_market():
    try:
        LiquidityMesh().venues("NOPE")
        assert False
    except ValueError:
        pass
