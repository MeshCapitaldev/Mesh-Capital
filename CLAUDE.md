# Mesh Capital

## Overview
A unified liquidity layer for Solana. Builds a live depth graph of every venue (the **mesh**) and
routes each order across it via a **smart router** that splits the fill to minimize slippage. Trade
perps routed to the best venue, and park capital in auto-compounding vaults. Non-custodial: the mesh
routes, the user's wallet signs.

## Stack
- **Backend**: Python 3.11, Flask 3.0, httpx
- **Frontend**: Vue 3 + Vite
- **AI**: Anthropic Claude (primary), DeepInfra (fallback)

## Structure
```
backend/app/services/
  mesh.py            — live depth graph; each venue a constant-product pool [core]
  router.py          — marginal-price split across venues → lowest blended price [core]
  perp_engine.py     — perp positions routed to best mark+funding venue
  compound_vault.py  — auto-compounding vaults; APY = APR compounded N/yr
  solana_client.py   — USD prices
  registry.py        — shared singletons
```

## The smart router (core)
Splits an order into `ROUTER_SPLIT_STEPS` increments; each increment goes to whichever venue offers
the best marginal price given what's already routed there (marginal = k/remaining²). Converges to the
lowest blended price; provably beats the single deepest venue when ≥2 venues have depth. Returns the
split, blended price, price impact, and savings vs best single venue.

## API
- `POST /api/route/quote`   — `{market, side, size}` → optimal split + savings
- `GET  /api/mesh/<market>` — live depth across venues
- `POST /api/perp/open` · `POST /api/perp/<id>/close` · `GET /api/perp?wallet=`
- `GET  /api/vault` · `POST /api/vault/deposit`

## Dev
```bash
npm run dev      # both servers
pytest tests/ -v # no API keys needed
python backend/scripts/simulate.py  # routed fill vs single-venue, perp, vaults
```
Tests cover the router (split, beats-single-venue, deeper-venue-gets-more, savings scaling), the mesh
(depth, convex impact, marginal price), perps (routing, PnL), and vaults (APY > APR).

## Note on git
Commits authored anonymously as the project (no personal contributor).
