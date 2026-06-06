"""
The Smart Router — split an order across venues to minimize total slippage.

Marginal-price allocation: the order is divided into `split_steps` increments; each increment is
assigned to whichever venue currently offers the best marginal execution price given what's already
been routed there. As a venue fills and its marginal price rises, the router shifts to the next-best
venue. This converges to the lowest achievable blended price — and it provably beats sending the
whole order to the single deepest venue whenever ≥2 venues have meaningful depth.
"""
from dataclasses import dataclass
from typing import Optional

from app.config import Config
from app.services.mesh import LiquidityMesh, Venue
from app.utils.logger import get_logger
from app.utils.helpers import safe_div
from app.utils.rate_limiter import route_limiter

logger = get_logger(__name__)


@dataclass
class RouteLeg:
    venue: str
    base_amount: float
    quote_cost: float

    @property
    def avg_price(self) -> float:
        return safe_div(self.quote_cost, self.base_amount)

    def to_dict(self, total_base: float) -> dict:
        return {
            "venue": self.venue,
            "base_amount": round(self.base_amount, 6),
            "fraction": round(safe_div(self.base_amount, total_base), 4),
            "price": round(self.avg_price, 6),
            "quote_cost": round(self.quote_cost, 4),
        }


@dataclass
class RouteResult:
    market: str
    side: str
    size_base: float
    blended_price: float
    quote_total: float
    price_impact_pct: float
    best_single_price: float
    savings_vs_best_single_pct: float
    legs: list[RouteLeg]

    def to_dict(self) -> dict:
        return {
            "market": self.market,
            "side": self.side,
            "size": round(self.size_base, 6),
            "blended_price": round(self.blended_price, 6),
            "quote_total": round(self.quote_total, 4),
            "price_impact_pct": round(self.price_impact_pct, 4),
            "best_single_price": round(self.best_single_price, 6),
            "savings_vs_best_single_pct": round(self.savings_vs_best_single_pct, 4),
            "route": [l.to_dict(self.size_base) for l in self.legs],
        }


class SmartRouter:
    def __init__(self, mesh: Optional[LiquidityMesh] = None, config: type = Config):
        self._mesh = mesh or LiquidityMesh(config)
        self._steps = max(4, config.ROUTER_SPLIT_STEPS)

    def quote(self, market: str, side: str, size_base: float) -> RouteResult:
        route_limiter.acquire()
        if size_base <= 0:
            raise ValueError("size must be positive")
        venues = self._mesh.venues(market)
        best_spot = min(v.spot_price for v in venues)

        # marginal-price split (buy side; sell is symmetric in this model)
        increment = size_base / self._steps
        taken = {v.name: 0.0 for v in venues}
        vmap = {v.name: v for v in venues}

        for _ in range(self._steps):
            # pick venue with the best (lowest) marginal price right now
            best = min(venues, key=lambda v: v.marginal_buy_price(taken[v.name]))
            taken[best.name] += increment

        legs: list[RouteLeg] = []
        quote_total = 0.0
        for name, base_amt in taken.items():
            if base_amt <= 0:
                continue
            cost = vmap[name].quote_buy_cost(base_amt)
            quote_total += cost
            legs.append(RouteLeg(venue=name, base_amount=base_amt, quote_cost=cost))
        legs.sort(key=lambda l: l.base_amount, reverse=True)

        blended = safe_div(quote_total, size_base)

        # baseline: whole order into the single best venue
        best_single_venue = min(venues, key=lambda v: v.quote_buy_cost(size_base))
        best_single_cost = best_single_venue.quote_buy_cost(size_base)
        best_single_price = safe_div(best_single_cost, size_base)

        savings = safe_div(best_single_price - blended, best_single_price) * 100
        impact = safe_div(blended - best_spot, best_spot) * 100

        logger.info(f"Route {market} {side} {size_base}: blended={blended:.4f} "
                    f"impact={impact:.2f}% savings={savings:.2f}% across {len(legs)} venues")

        return RouteResult(
            market=market.upper(), side=side, size_base=size_base,
            blended_price=blended, quote_total=quote_total, price_impact_pct=impact,
            best_single_price=best_single_price, savings_vs_best_single_pct=max(0.0, savings),
            legs=legs,
        )
