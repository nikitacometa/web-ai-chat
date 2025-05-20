#!/bin/bash
set -e

echo "Starting frontend..."

# Navigate to the project root (assuming script is in a subdirectory like 'scripts')
cd "$(dirname "$0")/.."

# Clean Next.js cache
echo "Cleaning Next.js cache..."
rm -rf .next

# Install dependencies
echo "Installing frontend dependencies with pnpm..."
pnpm install

# Start the Next.js development server
echo "Launching Next.js dev server..."
pnpm dev 