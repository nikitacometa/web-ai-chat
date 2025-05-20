#!/bin/bash
set -e

echo "Starting backend..."

# Navigate to the backend directory
cd "$(dirname "$0")/../backend"

# Ensure pydantic-settings is installed and added to Pipfile
echo "Ensuring pydantic-settings is installed..."
pipenv install pydantic-settings

# Install other dependencies
echo "Installing backend dependencies..."
pipenv install --dev

# Start the FastAPI application with uvicorn
echo "Launching FastAPI app with uvicorn..."
pipenv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --app-dir .. 