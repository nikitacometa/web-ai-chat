from datetime import datetime
from typing import List, Optional, Literal
from beanie import Document, Link
from pydantic import Field, HttpUrl
from .user import User


class EnvironmentVariable(Document):
    key: str = Field(..., description="Environment variable name")
    value: str = Field(..., description="Environment variable value")
    description: Optional[str] = Field(None, description="Description of the variable")


AppType = Literal["research", "app", "image", "doc"]


class UserApp(Document):
    name: str = Field(..., description="Application name")
    type: AppType = Field(..., description="Type of the application")
    code: str = Field(..., description="HTML code content of the application")
    url: Optional[HttpUrl] = Field(None, description="Application URL (auto-generated)")
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
            "is_active",
            "type"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Research App",
                "type": "research",
                "code": "<html><body><h1>Research Content</h1></body></html>",
                "description": "A research application about AI agents",
                "required_env_vars": [
                    ["API_KEY", "Your OpenWeather API key"],
                    ["LOCATION", "Default location for weather data"]
                ],
                "is_active": True
            }
        } 