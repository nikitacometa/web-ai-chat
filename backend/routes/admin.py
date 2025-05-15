# POST /admin/reset endpoint
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Any
from ..models import AdminResetRequest, Round, TwitterUser
import os

router = APIRouter()

# This should be properly secured in production
def verify_admin_token(token: str) -> bool:
    expected_token = os.environ.get("ADMIN_API_TOKEN", "test_admin_token")
    return token == expected_token

@router.post("/reset", response_model=Dict[str, Any])
async def reset_game(request: AdminResetRequest):
    """
    Start a new game round with specified Twitter handles
    """
    try:
        # Verify admin token
        if not verify_admin_token(request.admin_token):
            raise HTTPException(status_code=401, detail="Invalid admin token")
            
        # In a real implementation, this would:
        # 1. Fetch Twitter profile data for the handles
        # 2. Create a new round in the database
        # 3. Generate an initial battle image
        
        # For demo purposes, we'll create a mock response
        # Mock Twitter avatar URLs - would be fetched from Twitter API
        left_avatar = f"https://unavatar.io/twitter/{request.left_handle}"
        right_avatar = f"https://unavatar.io/twitter/{request.right_handle}"
        
        current_time = datetime.now()
        initial_deadline = current_time + timedelta(minutes=20)  # 20 min initial deadline
        max_deadline = current_time + timedelta(hours=24)  # 24 hour max duration
        
        new_round = Round(
            id=1,  # Would be auto-generated in DB
            left_user=TwitterUser(
                handle=request.left_handle,
                avatar_url=left_avatar,
                display_name=request.left_handle  # Would be fetched from Twitter
            ),
            right_user=TwitterUser(
                handle=request.right_handle,
                avatar_url=right_avatar,
                display_name=request.right_handle  # Would be fetched from Twitter
            ),
            momentum=request.initial_momentum,
            pot_amount=0.0,
            start_time=current_time,
            current_deadline=initial_deadline,
            max_deadline=max_deadline,
            battle_image_url=None  # Would be generated
        )
        
        return {
            "success": True,
            "round": new_round,
            "message": "New round started successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start new round: {str(e)}")

