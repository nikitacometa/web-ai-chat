from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from beanie import PydanticObjectId
from app.models.user import User
from app.models.user_app import UserApp
from app.schemas.user_app import UserAppCreate, UserAppResponse, UserAppFilter, UserAppUpdate
from datetime import datetime
import os
import re
from pathlib import Path

router = APIRouter(prefix="/user-apps", tags=["user-apps"])

# Configuration for file paths
FILES_BASE_PATH = "/var/www/api-files"
BASE_URL = "https://aisatisfy.me"


def sanitize_filename(name: str) -> str:
    """Convert app name to a valid filename"""
    # Remove special characters and replace spaces with underscores
    filename = re.sub(r'[^\w\s-]', '', name.lower())
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename


def save_html_file(content: str, filename: str) -> str:
    """Save HTML content to file and return the file path"""
    os.makedirs(FILES_BASE_PATH, exist_ok=True)
    file_path = os.path.join(FILES_BASE_PATH, f"{filename}.html")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


def generate_app_url(app_type: str, filename: str) -> str:
    """Generate the URL for the app based on type"""
    return f"{BASE_URL}/{app_type}/{filename}"


@router.post("/", response_model=UserAppResponse)
async def create_user_app(app_data: UserAppCreate):
    """
    Create a new user application with HTML content.
    
    This endpoint creates a new app entry in the database and saves the HTML content to a file.
    """
    # First, find or create the user
    user = await User.find_one(User.telegram_id == app_data.telegram_id)
    if not user:
        user = User(
            telegram_id=app_data.telegram_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await user.save()
    
    # Generate filename and save HTML content
    filename = sanitize_filename(app_data.name)
    file_path = save_html_file(app_data.code, filename)
    
    # Generate URL based on app type
    app_url = generate_app_url(app_data.type, filename)
    
    # Create the user app
    user_app = UserApp(
        name=app_data.name,
        type=app_data.type,
        code=app_data.code,
        url=app_url,
        description=app_data.description,
        required_env_vars=app_data.required_env_vars,
        owner=user,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    await user_app.save()
    
    # Prepare response
    return UserAppResponse(
        id=str(user_app.id),
        name=user_app.name,
        type=user_app.type,
        code=user_app.code,
        url=user_app.url,
        description=user_app.description,
        required_env_vars=user_app.required_env_vars,
        is_active=user_app.is_active,
        created_at=user_app.created_at,
        updated_at=user_app.updated_at,
        owner_telegram_id=user.telegram_id
    )


@router.get("/user/{telegram_id}", response_model=List[UserAppResponse])
async def get_user_apps(telegram_id: str):
    """
    Get all apps for a specific user by their telegram ID.
    """
    user = await User.find_one(User.telegram_id == telegram_id)
    if not user:
        return []
    
    apps = await UserApp.find(UserApp.owner.id == user.id).to_list()
    
    response = []
    for app in apps:
        await app.fetch_link(UserApp.owner)
        response.append(UserAppResponse(
            id=str(app.id),
            name=app.name,
            type=app.type,
            code=app.code,
            url=app.url,
            description=app.description,
            required_env_vars=app.required_env_vars,
            is_active=app.is_active,
            created_at=app.created_at,
            updated_at=app.updated_at,
            owner_telegram_id=app.owner.telegram_id
        ))
    
    return response


@router.put("/{app_id}", response_model=UserAppResponse)
async def update_user_app(app_id: str, app_update: UserAppUpdate):
    """
    Update an existing user application.
    """
    try:
        app = await UserApp.get(app_id)
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
        
        await app.fetch_link(UserApp.owner)
        
        # Update fields if provided
        if app_update.name is not None:
            app.name = app_update.name
        
        if app_update.type is not None:
            app.type = app_update.type
        
        if app_update.code is not None:
            app.code = app_update.code
            # Save updated HTML content
            filename = sanitize_filename(app.name)
            save_html_file(app.code, filename)
            # Update URL if type changed
            app.url = generate_app_url(app.type, filename)
        
        if app_update.description is not None:
            app.description = app_update.description
        
        if app_update.required_env_vars is not None:
            app.required_env_vars = app_update.required_env_vars
        
        if app_update.is_active is not None:
            app.is_active = app_update.is_active
        
        app.updated_at = datetime.utcnow()
        await app.save()
        
        return UserAppResponse(
            id=str(app.id),
            name=app.name,
            type=app.type,
            code=app.code,
            url=app.url,
            description=app.description,
            required_env_vars=app.required_env_vars,
            is_active=app.is_active,
            created_at=app.created_at,
            updated_at=app.updated_at,
            owner_telegram_id=app.owner.telegram_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[UserAppResponse])
async def query_user_apps(
    telegram_id: Optional[str] = Query(None, description="Filter by telegram ID"),
    type: Optional[str] = Query(None, description="Filter by app type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    name_contains: Optional[str] = Query(None, description="Filter by name containing text"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return")
):
    """
    Query user applications with filtering options.
    
    This endpoint allows you to search for apps based on various criteria.
    """
    # Build query
    query_conditions = []
    
    if telegram_id:
        user = await User.find_one(User.telegram_id == telegram_id)
        if user:
            query_conditions.append(UserApp.owner.id == user.id)
        else:
            return []  # No user found with this telegram_id
    
    if type:
        query_conditions.append(UserApp.type == type)
    
    if is_active is not None:
        query_conditions.append(UserApp.is_active == is_active)
    
    if name_contains:
        query_conditions.append({"name": {"$regex": name_contains, "$options": "i"}})
    
    # Execute query
    if query_conditions:
        apps = await UserApp.find(*query_conditions).skip(skip).limit(limit).to_list()
    else:
        apps = await UserApp.find_all().skip(skip).limit(limit).to_list()
    
    # Prepare response
    response = []
    for app in apps:
        await app.fetch_link(UserApp.owner)
        response.append(UserAppResponse(
            id=str(app.id),
            name=app.name,
            type=app.type,
            code=app.code,
            url=app.url,
            description=app.description,
            required_env_vars=app.required_env_vars,
            is_active=app.is_active,
            created_at=app.created_at,
            updated_at=app.updated_at,
            owner_telegram_id=app.owner.telegram_id
        ))
    
    return response


@router.delete("/{app_id}")
async def delete_user_app(app_id: str):
    """
    Delete a user application.
    """
    try:
        app = await UserApp.get(app_id)
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Delete the HTML file
        filename = sanitize_filename(app.name)
        file_path = os.path.join(FILES_BASE_PATH, f"{filename}.html")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await app.delete()
        
        return {"message": "App deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 