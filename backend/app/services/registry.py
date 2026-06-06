"""Shared singletons so all blueprints operate on one mesh."""
from app.services.solana_client import SolanaClient
from app.services.mesh import LiquidityMesh
from app.services.router import SmartRouter
from app.services.perp_engine import PerpEngine
from app.services.compound_vault import CompoundVault

solana = SolanaClient()
mesh = LiquidityMesh()
router = SmartRouter(mesh)
perps = PerpEngine()
vaults = CompoundVault()
