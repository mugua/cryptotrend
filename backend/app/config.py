from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "CryptoTrend API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./cryptotrend.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300  # seconds

    # API Keys (all optional)
    etherscan_api_key: str = ""
    fred_api_key: str = ""
    whale_alert_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""

    # Rate limiting (requests per second)
    coingecko_rate_limit: float = 1.0
    binance_rate_limit: float = 5.0
    etherscan_rate_limit: float = 0.2
    fred_rate_limit: float = 0.5
    reddit_rate_limit: float = 1.0

    # Scheduler intervals
    price_update_interval_minutes: int = 5
    onchain_update_interval_hours: int = 1
    macro_update_interval_hours: int = 6
    report_generation_interval_hours: int = 24

    # Coins to track
    tracked_coins: list[str] = [
        "bitcoin",
        "ethereum",
        "binancecoin",
        "solana",
        "xrp",
        "cardano",
        "avalanche-2",
        "polkadot",
        "chainlink",
        "litecoin",
    ]
    binance_symbols: list[str] = ["BTCUSDT", "ETHUSDT"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
