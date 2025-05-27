# Deployment Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- Git

### Steps

1. **Clone the repository** (if not already done)
```bash
git clone <your-repo-url>
cd web-ai-chat
```

2. **Set up environment variables**
```bash
# Copy example files
cp .env.example .env
cp backend/.env.example backend/.env

# Edit the main .env file with your actual values:
# - AUTH_SECRET (generate with: openssl rand -base64 32)
# - XAI_API_KEY (from https://console.x.ai/)
# - BLOB_READ_WRITE_TOKEN (from Vercel Blob)
# - POSTGRES_URL (your PostgreSQL connection string)
# - REDIS_URL (your Redis connection string)
```

3. **Start the entire stack**
```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- FastAPI backend on port 8000
- Next.js web UI on port 3000

4. **Access the services**
- Web UI: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017

## Testing the Backend API

### Create a new app
```bash
curl -X POST "http://localhost:8000/api/v1/user-apps/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test App",
    "url": "https://example.com",
    "description": "A test application",
    "required_env_vars": [["API_KEY", "Your API key"]],
    "telegram_id": "123456789"
  }'
```

### Query apps
```bash
curl "http://localhost:8000/api/v1/user-apps/?telegram_id=123456789"
```

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js Web   │────▶│  FastAPI Backend │────▶│    MongoDB      │
│   Port: 3000    │     │   Port: 8000    │     │   Port: 27017   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Stopping the Services

```bash
docker-compose down

# To also remove volumes (database data):
docker-compose down -v
```

## Production Considerations

1. **Security**
   - Change default MongoDB credentials
   - Use strong AUTH_SECRET
   - Enable HTTPS
   - Restrict CORS origins

2. **Environment Variables**
   - Use proper secret management
   - Don't commit .env files
   - Use environment-specific configs

3. **Scaling**
   - Add nginx reverse proxy
   - Use MongoDB replica sets
   - Add Redis for caching
   - Consider Kubernetes for orchestration

4. **Monitoring**
   - Add logging aggregation
   - Set up health checks
   - Monitor resource usage
   - Set up alerts 