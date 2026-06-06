# Contributing to Mesh Capital

PRs welcome.

## Setup
```bash
git clone https://github.com/MeshCapital/MeshCapital.git
cd MeshCapital && cp .env.example .env
npm run setup
```

## Tests
```bash
pytest tests/ -v
```
Fully unit-tested with no API keys. The smart router, mesh depth, perp engine, and vaults are covered.

## Branches
`feature/`, `hotfix/`, `chore/`

## Commits
Conventional: `feat:`, `fix:`, `chore:`, `docs:`

## Roadmap
- Live on-chain pool state for the mesh (Raydium/Orca/Meteora/Phoenix) via RPC
- Real Jupiter-style route execution + transaction building
- Live perp venue state (Drift/Zeta/Mango) for true mark + funding routing
- Multi-hop routing across intermediate pairs
- MEV-aware ordering and slippage guards
- Real vault strategy adapters
