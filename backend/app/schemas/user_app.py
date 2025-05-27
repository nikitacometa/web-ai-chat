from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, Field


AppType = Literal["research", "app", "image", "doc"]


class UserAppCreate(BaseModel):
    name: str = Field(..., description="Application name")
    type: AppType = Field(..., description="Type of the application")
    code: str = Field(..., description="HTML code content")
    description: str = Field(..., description="Application description")
    required_env_vars: List[List[str]] = Field(
        default_factory=list,
        description="List of [key, description] pairs for required environment variables"
    )
    telegram_id: str = Field(..., description="Telegram ID of the app owner")


class UserAppUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AppType] = None
    code: Optional[str] = None
    description: Optional[str] = None
    required_env_vars: Optional[List[List[str]]] = None
    is_active: Optional[bool] = None


class UserAppResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    type: AppType
    code: str
    url: Optional[HttpUrl]
    description: str
    required_env_vars: List[List[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    owner_telegram_id: str
    
    class Config:
        populate_by_name = True


class UserAppFilter(BaseModel):
    telegram_id: Optional[str] = None
    type: Optional[AppType] = None
    is_active: Optional[bool] = None
    name_contains: Optional[str] = None 