from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Telegram Bot
    telegram_bot_token: str
    webhook_url: Optional[str] = None
    
    # Google Gemini API
    gemini_api_key: str
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Server Configuration
    domain_url: str = "https://aisatisfy.me"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # File Storage
    research_dir: str = "/var/www/aisatisfy.me/research"
    apps_dir: str = "/var/www/aisatisfy.me/apps"
    
    # Development
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_research_url(self, file_id: str) -> str:
        return f"{self.domain_url}/with-research/{file_id}"
    
    def get_app_url(self, file_id: str) -> str:
        return f"{self.domain_url}/with-app/{file_id}"


settings = Settings()