import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.anthropic.com/v1")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "claude-sonnet-4-6")
    DEEPINFRA_API_KEY: str = os.getenv("DEEPINFRA_API_KEY", "")
    DEEPINFRA_BASE_URL: str = os.getenv("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    DEEPINFRA_MODEL_NAME: str = os.getenv("DEEPINFRA_MODEL_NAME", "meta-llama/Meta-Llama-3.1-70B-Instruct")

    # Solana
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    SOLANA_WS_URL: str = os.getenv("SOLANA_WS_URL", "wss://api.mainnet-beta.solana.com")
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "")
    HELIUS_RPC_URL: str = os.getenv("HELIUS_RPC_URL", "")

    # Price data
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    COINGECKO_BASE_URL: str = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")

    # Mesh / router
    ROUTER_SPLIT_STEPS: int = int(os.getenv("ROUTER_SPLIT_STEPS", "50"))
    PERP_MAX_LEVERAGE: float = float(os.getenv("PERP_MAX_LEVERAGE", "20.0"))
    VAULT_COMPOUND_PERIODS: int = int(os.getenv("VAULT_COMPOUND_PERIODS", "365"))

    # Flask
    DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("FLASK_PORT", "5001"))

    SUPPORTED_MARKETS: list[str] = [
        m.strip() for m in os.getenv(
            "SUPPORTED_MARKETS", "SOL-USDC,BTC-USDC,ETH-USDC,WIF-USDC,JUP-USDC,JTO-USDC"
        ).split(",")
    ]

    @classmethod
    def validate(cls) -> None:
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required. Copy .env.example to .env")
