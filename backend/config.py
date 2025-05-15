from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ALGOD_NODE: str = "https://mainnet-api.algonode.cloud"
    ALGOD_TOKEN: str = ""
    HOT_WALLET_MNEMONIC: str = ""
    OPENAI_API_KEY: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    ADMIN_TOKEN: str = "verysecretadmintoken"

    ROUND_INACTIVITY_TIMEOUT_SEC: int = 1200  # 20 minutes
    MAX_ROUND_DURATION_SEC: int = 86400     # 24 hours
    BET_TIME_EXTENSION_SEC: int = 60        # 1 minute

    # For Supabase service key if needed for admin actions, keep separate
    # SUPABASE_SERVICE_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings() 