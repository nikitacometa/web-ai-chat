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
        # Avatar URLs are now provided directly in the request
        
        current_time = datetime.now()
        # Read from environment or use defaults for timeouts
        inactivity_timeout_minutes = int(os.environ.get("ROUND_INACTIVITY_TIMEOUT_MINUTES", "20"))
        max_duration_hours = int(os.environ.get("MAX_ROUND_DURATION_HOURS", "24"))

        initial_deadline = current_time + timedelta(minutes=inactivity_timeout_minutes)
        max_deadline = current_time + timedelta(hours=max_duration_hours)
        
        new_round = Round(
            id=1,  # Would be auto-generated in DB
            left_user=TwitterUser(
                handle="Left Player", # Or derive from URL if desired
                avatar_url=request.left_avatar_url,
                display_name="Left Player" # Or derive from URL
            ),
            right_user=TwitterUser(
                handle="Right Player", # Or derive from URL
                avatar_url=request.right_avatar_url,
                display_name="Right Player" # Or derive from URL
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

