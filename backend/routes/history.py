# GET /history endpoint
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..models import Round, Bet, TwitterUser

router = APIRouter()

@router.get("/rounds", response_model=List[Round])
async def get_past_rounds(limit: int = 10, offset: int = 0):
    """
    Get historical game rounds
    """
    try:
        # Mock data for development
        current_time = datetime.now()
        
        # Generate some mock historical rounds
        past_rounds = []
        for i in range(1, limit + 1):
            day_offset = i * 2  # Each round 2 days apart
            start_time = current_time - timedelta(days=day_offset)
            
            # Alternate winners for demo
            winner = "left" if i % 2 == 0 else "right"
            momentum = 0 if winner == "left" else 100
            
            round = Round(
                id=100 + i,
                left_user=TwitterUser(
                    handle="elonmusk",
                    avatar_url="https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
                    display_name="Elon Musk"
                ),
                right_user=TwitterUser(
                    handle="jack",
                    avatar_url="https://pbs.twimg.com/profile_images/1115644092329758721/AFjOr-K8_400x400.jpg",
                    display_name="Jack"
                ),
                momentum=momentum,
                pot_amount=1000.0 * i,  # Different pot amounts
                start_time=start_time,
                current_deadline=start_time + timedelta(hours=12),  # Ended after 12 hours in this example
                max_deadline=start_time + timedelta(hours=24),
                active=False,
                winner=winner,
                battle_image_url=f"https://example.com/battle_{100+i}.jpg"  # Mock image URLs
            )
            past_rounds.append(round)
            
        return past_rounds[offset:offset+limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve past rounds: {str(e)}")

@router.get("/bets/{round_id}", response_model=List[Bet])
async def get_round_bets(round_id: int, limit: int = 50, offset: int = 0):
    """
    Get bets for a specific round
    """
    try:
        # Mock data for development
        current_time = datetime.now()
        
        # Generate some mock bets
        bets = []
        for i in range(1, limit + 1):
            minute_offset = i * 5  # Each bet 5 minutes apart
            timestamp = current_time - timedelta(minutes=minute_offset)
            
            # Alternate sides for demo
            side = "left" if i % 2 == 0 else "right"
            
            # Mock spell phrases
            spells = [
                "wizards cast digital spells on blockchain tokens",
                "dragons fly through virtual markets with ease",
                "knights defend the crypto realm vigilantly",
                "mages conjure algorithmic trading patterns instantly",
                "oracles predict the future of finance accurately"
            ]
            spell_index = i % len(spells)
            
            bet = Bet(
                id=1000 + i,
                round_id=round_id,
                side=side,
                amount=0.1 * (i % 10 + 1),  # Varying amounts
                spell=spells[spell_index],
                wallet_address=f"ALGO{i:010d}WALLET",
                timestamp=timestamp,
                processed=True,
                tx_id=f"TX_{i:010d}"
            )
            bets.append(bet)
            
        return bets[offset:offset+limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bets: {str(e)}")

 