#!/bin/bash
# Script to run the AlgoFOMO Backend (FastAPI)

echo "🚀 Starting AlgoFOMO Backend..."

# Script is in project root. Paths will be relative to project root.

# Activate Python virtual environment (expected inside backend/venv)
VENV_PATH="backend/venv"
if [ -d "$VENV_PATH" ]; then
  echo "🐍 Activating Python virtual environment from $VENV_PATH..."
  source "$VENV_PATH/bin/activate"
elif [ -z "$VIRTUAL_ENV" ]; then # Check if a venv is already active
  echo "⚠️ Python virtual environment '$VENV_PATH' not found and no global venv active."
  echo "Please create it (e.g., python3 -m venv $VENV_PATH), activate it, and install dependencies from backend/requirements.txt"
  echo "If you have dependencies installed globally (not recommended), the script will try to proceed."
else
  echo "🐍 Using already active Python virtual environment: $VIRTUAL_ENV"
fi

# Check for .env file (expected inside backend/.env)
ENV_FILE_PATH="backend/.env"
if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "⚠️ WARNING: $ENV_FILE_PATH file not found."
    echo "Please create one (e.g., by copying .env.example and renaming/moving to $ENV_FILE_PATH), filling in your secrets."
    echo "Attempting to start server anyway, but it will likely fail to connect to services."
fi

echo "🔥 Launching Uvicorn server for FastAPI app (backend.main:app)..."
# Run from project root, so app is backend.main:app
# Use --reload-dir to specify the directory to watch for changes
uvicorn backend.main:app --reload --reload-dir backend --host 0.0.0.0 --port 8000

echo "🚪 Backend server process ended." 