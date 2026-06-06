#!/usr/bin/env python3
"""Show the smart router beating single-venue execution, then a perp + a vault."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.mesh import LiquidityMesh
from app.services.router import SmartRouter
from app.services.perp_engine import PerpEngine
from app.services.compound_vault import CompoundVault


def main():
    print("\nMesh Capital Simulation\n" + "=" * 60)

    mesh = LiquidityMesh()
    router = SmartRouter(mesh)

    print("\nRouting a large SOL-USDC buy across the mesh:")
    for size in [1000, 10000, 50000]:
        r = router.quote("SOL-USDC", "buy", size)
        legs = " · ".join(f"{l.venue} {l.to_dict(r.size_base)['fraction']*100:.0f}%" for l in r.legs)
        print(f"  {size:>6} SOL → blended {r.blended_price:.4f} | impact {r.price_impact_pct:.2f}% "
              f"| savings vs best single {r.savings_vs_best_single_pct:.2f}%")
        print(f"         route: {legs}")

    print("\nPerp routed to best venue:")
    perps = PerpEngine()
    pos = perps.open("wallet1", "SOL-USDC", "LONG", 5000, 5.0, base_price=150.0)
    print(f"  {pos.market} {pos.side} ${pos.size_usd} {pos.leverage}x → venue {pos.venue} @ {pos.entry_price:.4f}")
    closed = perps.close(pos.id, 156.0)
    print(f"  closed @ 156.0 → PnL ${closed.realized_pnl_usd}")

    print("\nCompound vaults:")
    vaults = CompoundVault()
    for v in vaults.list_vaults():
        print(f"  {v['vault']:<22} APR {v['apr']*100:5.1f}%  →  APY {v['apy']*100:5.1f}%")

    print("\n" + "=" * 60)
    print("The mesh splits orders to beat single-venue fills. That's the whole point.\n")


if __name__ == "__main__":
    main()
