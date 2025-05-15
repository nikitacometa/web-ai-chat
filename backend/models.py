# Pydantic models will be defined here, as per docs/backend_plan.md
# e.g., Round, Bet, BetRequest, AdminResetRequest

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from uuid import UUID

# Example structure, will be filled based on backend_plan.md
# class Round(BaseModel):
#     id: int
#     current_deadline: datetime
#     ...

# class Bet(BaseModel):
#     id: int
#     ... 

class TwitterUser(BaseModel):
    handle: str
    avatar_url: str
    display_name: Optional[str] = None

class Round(BaseModel):
    id: int
    left_user: TwitterUser
    right_user: TwitterUser
    momentum: int = 50  # 0-100 scale, 50 is the middle
    pot_amount: float = 0.0
    start_time: datetime
    current_deadline: datetime
    max_deadline: datetime  # 24 hours from start
    active: bool = True
    winner: Optional[Literal["left", "right"]] = None
    battle_image_url: Optional[str] = None

class BetRequest(BaseModel):
    round_id: int
    side: Literal["left", "right"]
    amount: float
    spell: str
    wallet_address: str
    
    @validator('spell')
    def validate_spell_length(cls, v):
        words = v.strip().split()
        if len(words) > 10:
            raise ValueError('Spell must be 10 words or less')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Bet amount must be greater than zero')
        return v

class Bet(BetRequest):
    id: int
    timestamp: datetime
    processed: bool = False
    tx_id: Optional[str] = None

class AdminResetRequest(BaseModel):
    left_avatar_url: str
    right_avatar_url: str
    # Optional: Could add display names if needed
    # left_display_name: Optional[str] = "Player 1"
    # right_display_name: Optional[str] = "Player 2"
    initial_momentum: int = Field(default=50, ge=0, le=100)
    admin_token: str

class GameState(BaseModel):
    round: Round
    recent_bets: List[Bet] = []
    total_bets_count: int = 0
    left_side_bets_amount: float = 0.0
    right_side_bets_amount: float = 0.0 