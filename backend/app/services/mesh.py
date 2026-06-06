"""
The Mesh — a live depth graph of every venue for a market.

Each venue is modeled as a constant-product pool (reserves), which gives a realistic price-impact
curve: a fill of size `q` moves the price the way it would on a real AMM. Venues differ in depth,
so the router has a genuine optimization to solve. Spot price = base_reserve_quote / base_reserve.
"""
from dataclasses import dataclass
from typing import Optional

from app.config import Config
from app.utils.logger import get_logger
from app.utils.helpers import safe_div

logger = get_logger(__name__)


@dataclass
class Venue:
    name: str
    base_reserve: float      # units of the base asset (e.g. SOL)
    quote_reserve: float     # units of quote (e.g. USDC)

    @property
    def spot_price(self) -> float:
        return safe_div(self.quote_reserve, self.base_reserve)

    @property
    def depth_quote(self) -> float:
        return self.quote_reserve

    def quote_buy_cost(self, base_out: float) -> float:
        """Quote cost (in quote units) to buy `base_out` base from this venue (x*y=k)."""
        if base_out <= 0 or base_out >= self.base_reserve:
            return float("inf")
        k = self.base_reserve * self.quote_reserve
        new_base = self.base_reserve - base_out
        new_quote = k / new_base
        return new_quote - self.quote_reserve

    def marginal_buy_price(self, base_already: float) -> float:
        """Marginal price for the next tiny unit of base, given `base_already` taken."""
        remaining = self.base_reserve - base_already
        if remaining <= 0:
            return float("inf")
        k = self.base_reserve * self.quote_reserve
        # d(quote)/d(base_out) at this point ≈ k / remaining^2
        return k / (remaining * remaining)

    def to_dict(self) -> dict:
        return {
            "venue": self.name,
            "spot_price": round(self.spot_price, 6),
            "depth_quote": round(self.depth_quote, 2),
            "base_reserve": round(self.base_reserve, 4),
        }


# Seed venue depths per market (base_reserve, quote_reserve). Different depths per venue so the
# router has something real to optimize. In production these come from live on-chain pool state.
def _seed_mesh() -> dict[str, list[Venue]]:
    # market -> list of venues with varying depth
    return {
        "SOL-USDC": [
            Venue("raydium", 60000, 60000 * 150),
            Venue("orca",    45000, 45000 * 150.1),
            Venue("meteora", 30000, 30000 * 150.2),
            Venue("phoenix", 18000, 18000 * 149.9),
        ],
        "BTC-USDC": [
            Venue("raydium", 40, 40 * 68000),
            Venue("orca",    25, 25 * 68050),
            Venue("meteora", 15, 15 * 68100),
        ],
        "ETH-USDC": [
            Venue("raydium", 800, 800 * 3500),
            Venue("orca",    500, 500 * 3502),
            Venue("meteora", 300, 300 * 3498),
        ],
        "WIF-USDC": [
            Venue("raydium", 900000, 900000 * 2.5),
            Venue("orca",    400000, 400000 * 2.51),
            Venue("meteora", 250000, 250000 * 2.49),
        ],
        "JUP-USDC": [
            Venue("raydium", 1200000, 1200000 * 1.2),
            Venue("orca",    700000, 700000 * 1.205),
        ],
        "JTO-USDC": [
            Venue("raydium", 500000, 500000 * 3.0),
            Venue("orca",    300000, 300000 * 3.01),
        ],
    }


class LiquidityMesh:
    def __init__(self, config: type = Config):
        self._mesh = _seed_mesh()
        self._config = config

    def venues(self, market: str) -> list[Venue]:
        venues = self._mesh.get(market.upper())
        if not venues:
            raise ValueError(f"Unsupported market: {market}")
        # return copies so routing simulation never mutates the live mesh
        return [Venue(v.name, v.base_reserve, v.quote_reserve) for v in venues]

    def depth(self, market: str) -> dict:
        vs = self.venues(market)
        total = sum(v.depth_quote for v in vs)
        return {
            "market": market.upper(),
            "venue_count": len(vs),
            "total_depth_quote": round(total, 2),
            "best_spot": round(min(v.spot_price for v in vs), 6),
            "venues": [v.to_dict() for v in vs],
        }
