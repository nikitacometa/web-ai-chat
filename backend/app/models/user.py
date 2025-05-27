from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class User(Document):
    telegram_id: str = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "telegram_id",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": "123456789",
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe"
            }
        } 