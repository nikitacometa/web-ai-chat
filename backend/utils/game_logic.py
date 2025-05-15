import math
import random

def calculate_bet_impact(amount: float, spell: str) -> float:
    """
    Calculates the impact of a bet based on its amount and spell.

    Formula from PRD:
    impact = min( log10(bet) * promptPw * rng(0.8-1.2), 10 )
    promptPw = (#power-words)/10 (clamp 0.5-1.5)

    Assumptions:
    - '#power-words' is interpreted as the total number of words in the spell.
    - 'bet' (amount) for log10 calculation is clamped to be >= 1.0 to avoid log(<=0) or negative results from log.
    """
    if amount <= 0:
        return 0.0 # No impact for zero or negative amounts

    # Calculate log_bet_term: log10(bet_amount)
    # Clamp amount to be at least 1.0 for log10 to ensure non-negative, non-error result.
    # log10(1) = 0. For amounts > 1, it's positive.
    log_bet_term = math.log10(max(1.0, amount))

    # Calculate prompt_power: (#power-words)/10, clamped between 0.5 and 1.5
    num_words = len(spell.strip().split())
    if num_words == 0: # Avoid division by zero if spell is empty, though Pydantic validator might catch
        prompt_power_raw = 0
    else:
        prompt_power_raw = num_words / 10.0
    
    prompt_power = min(max(0.5, prompt_power_raw), 1.5)

    # Random factor: rng(0.8-1.2)
    random_factor = random.uniform(0.8, 1.2)

    # Calculate impact
    calculated_impact = log_bet_term * prompt_power * random_factor

    # Final impact: min(calculated_impact, 10.0) and ensure it's not negative
    final_impact = max(0.0, min(calculated_impact, 10.0))
    
    return round(final_impact, 4) # Round to a reasonable number of decimal places 