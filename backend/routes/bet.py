# POST /bet endpoint
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Any
from ..models import BetRequest, Bet

router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
async def place_bet(bet_request: BetRequest):
    """
    Place a bet on the current game round
    """
    try:
        # In a real implementation, this would:
        # 1. Verify the round is active
        # 2. Process the Algorand transaction
        # 3. Update the game state (extend deadline, update momentum)
        # 4. Generate a new battle image if needed
        
        # For now, just return a mock successful response
        new_bet = Bet(
            **bet_request.dict(),
            id=1,
            timestamp=datetime.now(),
            processed=True,
            tx_id="MOCK_TX_" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        
        # Mock extending deadline and updating momentum
        momentum_shift = 5 if bet_request.side == "left" else -5
        new_momentum = min(100, max(0, 65 + momentum_shift))  # Mock current momentum is 65
        
        return {
            "success": True,
            "bet": new_bet,
            "new_momentum": new_momentum,
            "new_deadline": datetime.now() + timedelta(minutes=1),
            "message": "Bet placed successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place bet: {str(e)}") 