from datetime import datetime
from typing import List, Optional
from beanie import Document, Link
from pydantic import Field, HttpUrl
from .user import User


class EnvironmentVariable(Document):
    key: str = Field(..., description="Environment variable name")
    value: str = Field(..., description="Environment variable value")
    description: Optional[str] = Field(None, description="Description of the variable")


class UserApp(Document):
    name: str = Field(..., description="Application name")
    url: HttpUrl = Field(..., description="Application URL")
    description: str = Field(..., description="Application description text")
    required_env_vars: List[List[str]] = Field(
        default_factory=list,
        description="List of lists containing required environment variables"
    )
    owner: Link[User] = Field(..., description="Reference to the user who created this app")
    is_active: bool = Field(default=True, description="Whether the app is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_apps"
        indexes = [
            "owner",
            "created_at",
            "is_active"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Weather App",
                "url": "https://weather-app.example.com",
                "description": "A simple weather application that shows current weather",
                "required_env_vars": [
                    ["API_KEY", "Your OpenWeather API key"],
                    ["LOCATION", "Default location for weather data"]
                ],
                "is_active": True
            }
        } 