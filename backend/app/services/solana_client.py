from typing import Optional
import httpx

from app.config import Config
from app.utils.logger import get_logger
from app.utils.retry import retry
from app.utils.cache import price_cache
from app.utils.rate_limiter import coingecko_limiter

logger = get_logger(__name__)

COINGECKO_IDS = {
    "SOL": "solana", "BTC": "bitcoin", "ETH": "ethereum",
    "WIF": "dogwifcoin", "JUP": "jupiter-exchange-solana", "JTO": "jito-governance-token",
}


class SolanaClient:
    def __init__(self, config: type = Config):
        self._cg_base = config.COINGECKO_BASE_URL
        self._cg_key = config.COINGECKO_API_KEY
        self._http = httpx.Client(timeout=15.0)

    def close(self) -> None:
        self._http.close()

    @retry(max_attempts=3, delay=1.0)
    def get_price_usd(self, market: str) -> Optional[float]:
        base = market.split("-")[0].upper()
        cached = price_cache.get(f"usd:{base}")
        if cached is not None:
            return cached
        cg_id = COINGECKO_IDS.get(base)
        if not cg_id:
            return None
        coingecko_limiter.wait_and_acquire()
        headers = {"x-cg-demo-api-key": self._cg_key} if self._cg_key else {}
        resp = self._http.get(f"{self._cg_base}/simple/price",
                              params={"ids": cg_id, "vs_currencies": "usd"}, headers=headers)
        resp.raise_for_status()
        price = resp.json().get(cg_id, {}).get("usd")
        if price is not None:
            price_cache.set(f"usd:{base}", float(price))
        return float(price) if price is not None else None
