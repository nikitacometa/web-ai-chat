from supabase import create_client, Client
from app.core.config import settings
from typing import Optional, Dict, Any
import json
from datetime import datetime


class Database:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None) -> Dict[str, Any]:
        """Get or create user in database"""
        # Check if user exists
        result = self.client.table("users").select("*").eq("telegram_id", telegram_id).execute()
        
        if result.data:
            # Update last active
            user = result.data[0]
            self.client.table("users").update({
                "last_active": datetime.utcnow().isoformat(),
                "username": username or user.get("username")
            }).eq("id", user["id"]).execute()
            return user
        else:
            # Create new user
            new_user = {
                "telegram_id": telegram_id,
                "username": username,
                "created_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow().isoformat()
            }
            result = self.client.table("users").insert(new_user).execute()
            return result.data[0]
    
    async def save_command(
        self,
        user_id: int,
        command_type: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        file_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save command execution to database"""
        command = {
            "user_id": user_id,
            "command_type": command_type,
            "input_data": json.dumps(input_data),
            "output_data": json.dumps(output_data) if output_data else None,
            "file_url": file_url,
            "created_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("commands").insert(command).execute()
        return result.data[0]
    
    async def get_user_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current user state"""
        result = self.client.table("user_states").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    
    async def update_user_state(
        self,
        user_id: int,
        current_command: Optional[str] = None,
        last_command_id: Optional[int] = None,
        state_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user state"""
        state = {
            "user_id": user_id,
            "current_command": current_command,
            "last_command_id": last_command_id,
            "state_data": json.dumps(state_data) if state_data else None,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Check if state exists
        existing = await self.get_user_state(user_id)
        if existing:
            result = self.client.table("user_states").update(state).eq("user_id", user_id).execute()
        else:
            result = self.client.table("user_states").insert(state).execute()
        
        return result.data[0]
    
    async def get_last_command(self, user_id: int, command_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get last command for user"""
        query = self.client.table("commands").select("*").eq("user_id", user_id)
        if command_type:
            query = query.eq("command_type", command_type)
        
        result = query.order("created_at", desc=True).limit(1).execute()
        if result.data:
            command = result.data[0]
            # Parse JSON fields
            command["input_data"] = json.loads(command["input_data"]) if command["input_data"] else None
            command["output_data"] = json.loads(command["output_data"]) if command["output_data"] else None
            return command
        return None


db = Database()