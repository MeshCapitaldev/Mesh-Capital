<div align="center">

<img width="2172" height="724" alt="ChatGPT Image 6 Jun 2026, 17 34 42" src="https://github.com/user-attachments/assets/4670d185-b4bd-4cb0-a144-874deae011a0" />


**One liquidity layer for Solana. Trade perps, route deep liquidity, and compound on-chain — with sub-second fills and self-custody by default.**

*Solana's liquidity is fragmented across a dozen venues. Mesh weaves it into one.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![CI](https://github.com/MeshCapital/MeshCapital/actions/workflows/ci.yml/badge.svg)](https://github.com/MeshCapital/MeshCapital/actions)
[![Solana](https://img.shields.io/badge/Solana-mainnet-9945FF.svg)](https://solana.com/)

[Quickstart](#quickstart) · [How it works](#how-it-works) · [The router](#the-smart-router) · [API](#api-reference)

</div>

---

## Why Mesh Capital exists

Solana has some of the deepest liquidity in crypto — and it's scattered. Spot is split across
Raydium, Orca, Meteora, Phoenix, and a Jupiter route on top. Perps live on Drift, Zeta, Mango.
Yield sits in a dozen vaults. Every venue shows you only its own slice, so a single large order
slams one pool, eats the slippage, and leaves better prices sitting untouched one tab over.

Mesh Capital treats all of that as **one surface.**

It builds a live graph of every venue's depth — the **mesh** — and routes each order across it so a
fill is split to wherever execution is actually best, not just where you happened to be looking.
Trade perps through the same layer and the order is routed to the venue offering the best mark and
funding at that instant. Park capital and it auto-compounds on-chain. Everything is non-custodial:
the mesh routes, your keys sign, your funds never leave your wallet.

The result is the execution you'd get from running your own smart order router across the whole
ecosystem — as a single layer, with sub-second fills.

---

## How it works

```
              your order (size, side, market)
                          │
              ┌───────────▼────────────┐
              │       The Mesh          │  live depth graph across every venue
              │  Raydium · Orca · Drift │
              │  Zeta · Meteora · Mango │
              └───────────┬────────────┘
                          │
              ┌───────────▼────────────┐
              │     Smart Router        │  split the order across venues to
              │  marginal-price split   │  minimize total slippage
              └───────────┬────────────┘
                          │  best effective price, sub-second
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   Spot routing      Perp routing      Compound vault
   (best fill)       (best mark+fund)  (auto-compounding)
```

---

## The smart router

This is the core of Mesh. A naive trade sends the whole order to one venue and pays whatever
slippage that pool's depth implies. The router does better: it splits the order across venues by
**marginal execution price.**

It allocates the order in small increments, and each increment goes to whichever venue currently
offers the best *marginal* price given what's already been routed there. As a venue fills up and
its price impact rises, the router shifts to the next-best venue — until the whole order is placed
at the lowest achievable blended price. Splitting a large order across three medium pools routinely
beats dumping it into the single deepest one.

Every routed fill returns the **split** (how much went where), the **blended price**, the **price
impact**, and the **savings vs. the best single venue** — so the routing is never a black box.

```json
{
  "market": "SOL-USDC",
  "side": "buy",
  "size": 50000,
  "blended_price": 150.42,
  "price_impact_pct": 0.18,
  "savings_vs_best_single_pct": 0.46,
  "route": [
    { "venue": "raydium", "fraction": 0.41, "price": 150.39 },
    { "venue": "orca",    "fraction": 0.33, "price": 150.43 },
    { "venue": "meteora", "fraction": 0.26, "price": 150.47 }
  ]
}
```

---

## Quickstart

### Docker

```bash
git clone https://github.com/MeshCapital/MeshCapital.git
cd MeshCapital
cp .env.example .env
docker compose up
```

Dashboard: http://localhost:3000 · API: http://localhost:5001

### Manual

```bash
cd backend && pip install -e . && python run.py
cd frontend && npm install && npm run dev
```

---

## Configuration

```env
LLM_API_KEY=your_key
LLM_MODEL_NAME=claude-sonnet-4-6
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

ROUTER_SPLIT_STEPS=50          # granularity of the marginal-price split
PERP_MAX_LEVERAGE=20.0
VAULT_COMPOUND_PERIODS=365     # compounding frequency per year
```

---

## API reference

| Method | Endpoint | Body / Params | Returns |
|--------|----------|---------------|---------|
| `POST` | `/api/route/quote` | `{market, side, size}` | the optimal split + blended price + savings |
| `GET`  | `/api/mesh/<market>` | — | live depth across every venue for a market |
| `POST` | `/api/perp/open` | `{market, side, size_usd, leverage}` | routed perp position |
| `POST` | `/api/perp/<id>/close` | — | close + realized PnL |
| `GET`  | `/api/perp?wallet=` | — | open positions |
| `GET`  | `/api/vault` | — | compounding vaults + live APY |
| `POST` | `/api/vault/deposit` | `{wallet, vault, amount}` | vault position |

---

## Self-custody

Mesh is a routing and accounting layer, not a custodian. It computes the optimal route and builds
the transactions; signing stays with the user's wallet and funds never sit in a protocol-controlled
account. The router is the brain — your keys are the authority.

---

## Project structure

```
meshcapital/
├── backend/
│   ├── app/
│   │   ├── api/        # route, mesh, perp, vault endpoints
│   │   ├── models/     # Route, Venue, PerpPosition, Vault
│   │   ├── services/   # liquidity mesh, smart router, perp engine, compound vault, agent
│   │   └── utils/      # logger, cache, rate limiter, retry, helpers
│   └── scripts/        # simulate a routed fill vs single-venue
├── frontend/           # Vue dashboard: route, mesh depth, perps, vaults
└── tests/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built on Solana. Fragmented liquidity, woven into one layer. Self-custody by default.</sub>
</div>
