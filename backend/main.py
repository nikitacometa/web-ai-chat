from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import admin, bet, history, state

app = FastAPI(
    title="AlgoFOMO Backend",
    description="API for the AlgoFOMO game.",
    version="0.1.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to AlgoFOMO API"}

# Include all implemented routes
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(bet.router, prefix="/bet", tags=["Betting"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(state.router, prefix="/state", tags=["Game State"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 