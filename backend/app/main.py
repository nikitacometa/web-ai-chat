from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database.connection import init_db
from app.routes import user_apps


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_apps.router, prefix=settings.API_V1_STR)

# Import and include generated content router
from app.routes import generated_content
app.include_router(generated_content.router)


@app.get("/")
async def root():
    return {"message": "AI Chat Backend API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"} 