from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from datetime import datetime
import json

router = APIRouter()

class ContentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

# Base directory for storing generated content
CONTENT_BASE_DIR = os.getenv("CONTENT_BASE_DIR", "/var/www/aisatisfy.me/content")
APPS_DIR = os.path.join(CONTENT_BASE_DIR, "apps")
RESEARCH_DIR = os.path.join(CONTENT_BASE_DIR, "research")

# Create directories if they don't exist
os.makedirs(APPS_DIR, exist_ok=True)
os.makedirs(RESEARCH_DIR, exist_ok=True)


@router.post("/api/v1/content/app")
async def create_app_content(request: ContentRequest):
    """Save generated app HTML content and return ID"""
    try:
        # Generate unique ID
        content_id = str(uuid.uuid4())[:8]
        
        # Save HTML file
        file_path = os.path.join(APPS_DIR, f"{content_id}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(request.content)
        
        # Save metadata if provided
        if request.metadata:
            meta_path = os.path.join(APPS_DIR, f"{content_id}.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(request.metadata, f)
        
        return {
            "success": True,
            "id": content_id,
            "url": f"https://aisatisfy.me/app/{content_id}",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/content/research")
async def create_research_content(request: ContentRequest):
    """Save generated research HTML content and return ID"""
    try:
        # Generate unique ID
        content_id = str(uuid.uuid4())[:8]
        
        # Save HTML file
        file_path = os.path.join(RESEARCH_DIR, f"{content_id}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(request.content)
        
        # Save metadata if provided
        if request.metadata:
            meta_path = os.path.join(RESEARCH_DIR, f"{content_id}.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(request.metadata, f)
        
        return {
            "success": True,
            "id": content_id,
            "url": f"https://aisatisfy.me/research/{content_id}",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/content/app/{content_id}")
async def get_app_content(content_id: str):
    """Retrieve app HTML content by ID"""
    file_path = os.path.join(APPS_DIR, f"{content_id}.html")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="App not found")
    
    return FileResponse(file_path, media_type="text/html")


@router.get("/api/v1/content/research/{content_id}")
async def get_research_content(content_id: str):
    """Retrieve research HTML content by ID"""
    file_path = os.path.join(RESEARCH_DIR, f"{content_id}.html")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Research not found")
    
    return FileResponse(file_path, media_type="text/html")


@router.get("/api/v1/content/list")
async def list_content(
    content_type: Optional[str] = None,
    limit: int = 50
):
    """List recent generated content"""
    try:
        items = []
        
        # Get apps if requested or no type specified
        if content_type in [None, "app"]:
            for filename in os.listdir(APPS_DIR)[:limit]:
                if filename.endswith(".html"):
                    content_id = filename[:-5]
                    file_path = os.path.join(APPS_DIR, filename)
                    stat = os.stat(file_path)
                    items.append({
                        "id": content_id,
                        "type": "app",
                        "url": f"https://aisatisfy.me/app/{content_id}",
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "size": stat.st_size
                    })
        
        # Get research if requested or no type specified
        if content_type in [None, "research"]:
            for filename in os.listdir(RESEARCH_DIR)[:limit]:
                if filename.endswith(".html"):
                    content_id = filename[:-5]
                    file_path = os.path.join(RESEARCH_DIR, filename)
                    stat = os.stat(file_path)
                    items.append({
                        "id": content_id,
                        "type": "research",
                        "url": f"https://aisatisfy.me/research/{content_id}",
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "size": stat.st_size
                    })
        
        # Sort by creation time
        items.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "items": items[:limit],
            "total": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))