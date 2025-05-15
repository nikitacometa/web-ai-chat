# Authentication utilities, e.g., for admin token checking

# from fastapi import HTTPException, Security
# from fastapi.security import APIKeyHeader
# from ..config import settings

# API_KEY_NAME = "Authorization"
# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# async def get_admin_user(api_key: str = Security(api_key_header)):
#     if api_key == f"Bearer {settings.ADMIN_TOKEN}":
#         return True
#     raise HTTPException(status_code=403, detail="Could not validate credentials") 