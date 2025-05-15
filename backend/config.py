from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ALGOD_NODE: str = "https://mainnet-api.algonode.cloud"
    ALGOD_TOKEN: str = ""
    HOT_WALLET_MNEMONIC: str = ""
    OPENAI_API_KEY: str = ""
    SUPABASE_URL: str = "https://itpzxmkjaqnahoqtzcml.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml0cHp4bWtqYXFuYWhvcXR6Y21sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDczMzYwNTYsImV4cCI6MjA2MjkxMjA1Nn0.hwwOmCJFlPICU7SPcoeQO2ZOo09P7cAZa7iulFqJIek"
    ADMIN_TOKEN: str = "verysecretadmintoken"

    ROUND_INACTIVITY_TIMEOUT_SEC: int = 1200  # 20 minutes
    MAX_ROUND_DURATION_SEC: int = 86400     # 24 hours
    BET_TIME_EXTENSION_SEC: int = 60        # 1 minute

    # For Supabase service key if needed for admin actions, keep separate
    # SUPABASE_SERVICE_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings() 