# GET /state endpoint
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from ..models import GameState, Round, TwitterUser

router = APIRouter()

# This would be replaced with database calls in the real implementation
async def get_mock_game_state():
    # For development purposes, create a mock game state
    current_time = datetime.now()
    
    mock_round = Round(
        id=1,
        left_user=TwitterUser(
            handle="elonmusk",
            avatar_url="https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
            display_name="Elon Musk"
        ),
        right_user=TwitterUser(
            handle="SBF_FTX",
            avatar_url="https://pbs.twimg.com/profile_images/1590968738358079488/IY9Gx6Ok_400x400.jpg",
            display_name="SBF"
        ),
        momentum=65,
        pot_amount=12345.67,
        start_time=current_time - timedelta(hours=1),
        current_deadline=current_time + timedelta(minutes=30),
        max_deadline=current_time + timedelta(hours=23),
        battle_image_url=None
    )
    
    return GameState(round=mock_round)

@router.get("/", response_model=GameState)
async def get_current_state():
    """
    Get the current game state including active round and recent bets
    """
    try:
        game_state = await get_mock_game_state()
        return game_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve game state: {str(e)}") 