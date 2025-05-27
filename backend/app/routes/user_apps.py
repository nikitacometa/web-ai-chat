from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from beanie import PydanticObjectId
from app.models.user import User
from app.models.user_app import UserApp
from app.schemas.user_app import UserAppCreate, UserAppResponse, UserAppFilter
from datetime import datetime

router = APIRouter(prefix="/user-apps", tags=["user-apps"])


@router.post("/", response_model=UserAppResponse)
async def create_user_app(app_data: UserAppCreate):
    """
    Create a new user application.
    
    This endpoint creates a new app entry in the database with the provided details.
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
    
    # Create the user app
    user_app = UserApp(
        name=app_data.name,
        url=str(app_data.url),
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
        url=user_app.url,
        description=user_app.description,
        required_env_vars=user_app.required_env_vars,
        is_active=user_app.is_active,
        created_at=user_app.created_at,
        updated_at=user_app.updated_at,
        owner_telegram_id=user.telegram_id
    )


@router.get("/", response_model=List[UserAppResponse])
async def query_user_apps(
    telegram_id: Optional[str] = Query(None, description="Filter by telegram ID"),
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
            url=app.url,
            description=app.description,
            required_env_vars=app.required_env_vars,
            is_active=app.is_active,
            created_at=app.created_at,
            updated_at=app.updated_at,
            owner_telegram_id=app.owner.telegram_id
        ))
    
    return response 