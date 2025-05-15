#!/bin/bash
# Script to run the AlgoFOMO Frontend (Next.js)

echo "🎨 Starting AlgoFOMO Frontend..."

# Check for node_modules directory
if [ ! -d "node_modules" ]; then
    echo "⚠️ node_modules directory not found."
    echo "Please run 'pnpm install' (or npm/yarn install) to install dependencies first."
    # Optionally, attempt to run pnpm install if pnpm is found
    # if command -v pnpm &> /dev/null; then
    #   echo "⚙️ Attempting to install dependencies with pnpm..."
    #   pnpm install || { echo "❌ pnpm install failed!"; exit 1; }
    # else
    #   exit 1 # Exit if node_modules not found and cannot install
    # fi
fi

# Check for .env.local file for frontend-specific environment variables
if [ ! -f ".env.local" ]; then
    echo "⚠️ WARNING: .env.local file not found in project root."
    echo "The frontend might not connect to the backend correctly without NEXT_PUBLIC_API_URL."
    echo "You can create one by copying relevant parts from .env.example."
fi

echo "🌐 Launching Next.js development server with pnpm dev..."
# Ensure pnpm is installed and your package.json has a "dev" script
pnpm dev

echo "🚪 Frontend server process ended." 