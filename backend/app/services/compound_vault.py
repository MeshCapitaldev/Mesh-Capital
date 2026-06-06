"""
Compound vaults — auto-compounding on-chain yield positions.

Each vault has a base APR from the underlying strategy; the effective APY is the APR compounded
`compound_periods` times per year. Deposits accrue value continuously at the compounded rate.
"""
import time
import math
from dataclasses import dataclass, field
from typing import Optional

from app.config import Config
from app.utils.logger import get_logger
from app.utils.helpers import new_id, utcnow_iso, safe_div

logger = get_logger(__name__)

_positions: dict[str, "VaultPosition"] = {}
SECONDS_PER_YEAR = 365 * 24 * 3600

# vault -> base APR from the strategy
VAULTS = {
    "sol-staking": 0.072,
    "usdc-lending": 0.11,
    "lp-meteora-sol-usdc": 0.24,
    "jlp": 0.35,
}


def apy_from_apr(apr: float, periods: int) -> float:
    return (1 + apr / periods) ** periods - 1


@dataclass
class VaultPosition:
    id: str
    wallet: str
    vault: str
    deposited: float
    apr: float
    opened_ts: float = field(default_factory=time.time)
    opened_at: str = field(default_factory=utcnow_iso)

    def value(self, periods: int, now_ts: Optional[float] = None) -> float:
        elapsed_years = max(0.0, ((now_ts or time.time()) - self.opened_ts) / SECONDS_PER_YEAR)
        rate = apy_from_apr(self.apr, periods)
        return self.deposited * ((1 + rate) ** elapsed_years)

    def to_dict(self, periods: int) -> dict:
        return {
            "id": self.id, "wallet": self.wallet, "vault": self.vault,
            "deposited": round(self.deposited, 6), "apr": round(self.apr, 4),
            "apy": round(apy_from_apr(self.apr, periods), 4),
            "current_value": round(self.value(periods), 6),
            "opened_at": self.opened_at,
        }


class CompoundVault:
    def __init__(self, config: type = Config):
        self._periods = config.VAULT_COMPOUND_PERIODS

    def list_vaults(self) -> list[dict]:
        return [
            {"vault": name, "apr": round(apr, 4), "apy": round(apy_from_apr(apr, self._periods), 4)}
            for name, apr in VAULTS.items()
        ]

    def deposit(self, wallet: str, vault: str, amount: float) -> VaultPosition:
        if vault not in VAULTS:
            raise ValueError(f"Unknown vault: {vault}")
        if amount <= 0:
            raise ValueError("amount must be positive")
        pos = VaultPosition(id=new_id(), wallet=wallet, vault=vault,
                            deposited=amount, apr=VAULTS[vault])
        _positions[pos.id] = pos
        logger.info(f"Vault deposit: {wallet[:8]} {amount} → {vault} "
                    f"(APY {apy_from_apr(VAULTS[vault], self._periods)*100:.1f}%)")
        return pos

    def get(self, position_id: str) -> Optional[dict]:
        pos = _positions.get(position_id)
        return pos.to_dict(self._periods) if pos else None

    def list_for_wallet(self, wallet: str) -> list[dict]:
        return [p.to_dict(self._periods) for p in _positions.values() if p.wallet == wallet]

    @property
    def periods(self) -> int:
        return self._periods
