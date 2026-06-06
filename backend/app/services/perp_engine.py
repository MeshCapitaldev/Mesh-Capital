"""
Perp engine — routes perp positions to the best venue by mark + funding, tracks PnL.
A thin layer over a set of perp venues; the position is "routed" to whichever venue offers the
best entry (tightest mark, most favorable funding for the side).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.config import Config
from app.utils.logger import get_logger
from app.utils.helpers import new_id, utcnow_iso, pct_change, short_id

logger = get_logger(__name__)

_positions: dict[str, "PerpPosition"] = {}

# perp venues with a mark offset + funding (per side). In production from live venue state.
PERP_VENUES = {
    "drift": {"mark_offset": 0.0000, "funding_8h": 0.0001},
    "zeta":  {"mark_offset": 0.0003, "funding_8h": -0.0001},
    "mango": {"mark_offset": 0.0002, "funding_8h": 0.0002},
}


class PerpStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class PerpPosition:
    id: str
    wallet: str
    market: str
    side: str
    size_usd: float
    leverage: float
    venue: str
    entry_price: float
    opened_at: str = field(default_factory=utcnow_iso)
    status: PerpStatus = PerpStatus.OPEN
    closed_at: Optional[str] = None
    exit_price: Optional[float] = None
    realized_pnl_usd: Optional[float] = None

    def pnl(self, current: float) -> float:
        raw = pct_change(self.entry_price, current) / 100
        lev = raw * self.leverage if self.side == "LONG" else -raw * self.leverage
        return self.size_usd * lev

    def to_dict(self, current_price: Optional[float] = None) -> dict:
        d = {
            "id": self.id, "wallet": self.wallet, "market": self.market, "side": self.side,
            "size_usd": self.size_usd, "leverage": self.leverage, "venue": self.venue,
            "entry_price": self.entry_price, "status": self.status.value,
            "opened_at": self.opened_at, "closed_at": self.closed_at,
            "exit_price": self.exit_price, "realized_pnl_usd": self.realized_pnl_usd,
        }
        if current_price is not None and self.status == PerpStatus.OPEN:
            d["unrealized_pnl_usd"] = round(self.pnl(current_price), 4)
        return d


class PerpEngine:
    def __init__(self, config: type = Config):
        self._max_lev = config.PERP_MAX_LEVERAGE

    def best_venue(self, market: str, side: str, base_price: float) -> tuple[str, float]:
        """Pick the venue with the best entry for this side (tightest effective mark)."""
        best_name, best_mark = None, None
        for name, v in PERP_VENUES.items():
            mark = base_price * (1 + v["mark_offset"])
            # longs prefer lower mark + negative funding; shorts the opposite
            score = mark + (v["funding_8h"] * base_price if side == "LONG" else -v["funding_8h"] * base_price)
            if best_mark is None or score < best_mark:
                best_name, best_mark = name, score
                best_entry = mark
        return best_name, best_entry

    def open(self, wallet: str, market: str, side: str, size_usd: float,
             leverage: float, base_price: float) -> PerpPosition:
        side = side.upper()
        if leverage > self._max_lev:
            raise ValueError(f"Leverage exceeds max ({self._max_lev}x)")
        if size_usd <= 0:
            raise ValueError("size must be positive")
        venue, entry = self.best_venue(market, side, base_price)
        pos = PerpPosition(id=new_id(), wallet=wallet, market=market.upper(), side=side,
                           size_usd=size_usd, leverage=leverage, venue=venue, entry_price=entry)
        _positions[pos.id] = pos
        logger.info(f"Perp open: {short_id(pos.id)} {market} {side} ${size_usd} {leverage}x "
                    f"routed to {venue} @ {entry:.4f}")
        return pos

    def close(self, position_id: str, exit_price: float) -> Optional[PerpPosition]:
        pos = _positions.get(position_id)
        if not pos or pos.status != PerpStatus.OPEN:
            return pos
        pos.realized_pnl_usd = round(pos.pnl(exit_price), 4)
        pos.exit_price = exit_price
        pos.status = PerpStatus.CLOSED
        pos.closed_at = utcnow_iso()
        logger.info(f"Perp close: {short_id(pos.id)} pnl=${pos.realized_pnl_usd}")
        return pos

    def get(self, position_id: str) -> Optional[PerpPosition]:
        return _positions.get(position_id)

    def list_for_wallet(self, wallet: str) -> list[PerpPosition]:
        return [p for p in _positions.values() if p.wallet == wallet]
