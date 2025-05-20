import pytest
from httpx import AsyncClient
from unittest import mock
from fastapi import BackgroundTasks

# Assuming your settings will provide a predictable ADMIN_TOKEN for tests
# For now, using the default from your config.py
ADMIN_TOKEN = "kek" 

@pytest.mark.asyncio
async def test_start_custom_game(test_client: AsyncClient):
    """Test the /admin/start_game endpoint success case."""
    start_game_payload = {
        "left_player_handle": "TestLeftHandle",
        "left_player_avatar_url": "http://example.com/left.png",
        "left_player_display_name": "Test Left Player",
        "right_player_handle": "TestRightHandle",
        "right_player_avatar_url": "http://example.com/right.png",
        "right_player_display_name": "Test Right Player",
        "initial_momentum": 60,
        "initial_spell_prompt": "A glorious test battle begins!",
        "admin_token": ADMIN_TOKEN
    }

    with mock.patch.object(BackgroundTasks, "add_task") as mock_add_task:
        response = await test_client.post("/admin/start_game", json=start_game_payload)
    
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    response_data = response.json()

    assert "id" in response_data, "Response should contain a round ID."
    assert response_data["active"] is True, "Newly started round should be active."
    assert response_data["momentum"] == 60, "Momentum should match payload."
    assert response_data["left_user"]["avatar_url"] == "http://example.com/left.png"
    assert response_data["right_user"]["avatar_url"] == "http://example.com/right.png"

    # Check if background task for image generation was called
    mock_add_task.assert_called_once()
    # Optionally, check the arguments of the call to trigger_render_battle_image
    args, kwargs = mock_add_task.call_args
    assert kwargs.get("round_id") == response_data["id"]
    assert "Test Left Player vs Test Right Player" in kwargs.get("custom_prompt", "")
    assert "A glorious test battle begins!" in kwargs.get("custom_prompt", "")

@pytest.mark.asyncio
async def test_start_custom_game_invalid_token(test_client: AsyncClient):
    """Test /admin/start_game with an invalid admin token."""
    start_game_payload = {
        "left_player_handle": "TestLeft",
        "left_player_avatar_url": "http://example.com/left.png",
        "right_player_handle": "TestRight",
        "right_player_avatar_url": "http://example.com/right.png",
        "initial_momentum": 50,
        "admin_token": "invalid_dummy_token"
    }
    response = await test_client.post("/admin/start_game", json=start_game_payload)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}. Response: {response.text}" 