# OpenAI API interactions
# e.g., generating images with DALL-E

# import openai
# from ..config import settings

# openai.api_key = settings.OPENAI_API_KEY

# async def generate_image(prompt: str):
#     pass 

import logging
from typing import Optional
import random
import asyncio

from openai import AsyncOpenAI
from ..config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client if API key is available
# Use AsyncOpenAI for FastAPI
if settings.OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
else:
    client = None
    logger.warning("OPENAI_API_KEY not found in settings. OpenAI service will use mock responses or fail.")

async def generate_battle_image_url(prompt: str, round_id: int) -> Optional[str]:
    """
    Generates a battle image URL based on a prompt using OpenAI DALL-E 3.
    Falls back to a mock if OpenAI client is not initialized or API call fails.
    """
    if not client:
        logger.warning(f"OpenAI client not initialized. Falling back to mock image for round {round_id}.")
        random_seed = random.randint(1, 1000)
        return f"https://picsum.photos/seed/{round_id}_{random_seed}/600/338"

    logger.info(f"[OpenAI Service] Requesting DALL-E 3 image for round {round_id} with prompt: '{prompt[:200]}...'")
    
    try:
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024", # DALL-E 3 supports 1024x1024, 1792x1024, or 1024x1792
            quality="standard", # or "hd"
            n=1,
            response_format="url" # Request a URL directly
        )
        
        image_url = response.data[0].url
        if image_url:
            logger.info(f"[OpenAI Service] Generated DALL-E 3 image URL: {image_url}")
            return image_url
        else:
            logger.error(f"[OpenAI Service] DALL-E 3 API call succeeded but no image URL returned for round {round_id}.")
            return None # Or fallback to mock

    except Exception as e:
        logger.error(f"[OpenAI Service] Error generating image with DALL-E 3 for round {round_id}: {e}", exc_info=True)
        # Fallback to mock image on error
        logger.warning(f"Falling back to mock image for round {round_id} due to OpenAI API error.")
        random_seed = random.randint(1000, 2000) # Different seed range for fallback
        return f"https://picsum.photos/seed/{round_id}_{random_seed}/600/338"

async def get_image_generation_status(job_id: str) -> Optional[dict]:
    """
    MOCK: Simulates checking the status of an image generation job.
    A real service might have asynchronous job processing. For DALL-E 3 with response_format="url",
    the URL is returned directly, so a status check like this might not be as relevant unless using batch API.
    """
    logger.info(f"[MOCK OpenAI Service] Checking status for job_id: {job_id} (mock always returns completed)")
    return {
        "job_id": job_id,
        "status": "completed",
        "result_url": f"https://picsum.photos/seed/{job_id}/600/338"
    } 