# AI Chat Backend API

A FastAPI backend service with MongoDB for managing user applications.

## Features

- FastAPI with async support
- MongoDB with Beanie ODM
- Two main endpoints for testing
- Docker support
- CORS enabled for frontend integration

## API Endpoints

### 1. Create User App
**POST** `/api/v1/user-apps/`

Creates a new user application in the database.

Request body:
```json
{
  "name": "My Weather App",
  "url": "https://weather-app.example.com",
  "description": "A simple weather application",
  "required_env_vars": [
    ["API_KEY", "Your OpenWeather API key"],
    ["LOCATION", "Default location for weather"]
  ],
  "telegram_id": "123456789"
}
```

Response:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "My Weather App",
  "url": "https://weather-app.example.com",
  "description": "A simple weather application",
  "required_env_vars": [
    ["API_KEY", "Your OpenWeather API key"],
    ["LOCATION", "Default location for weather"]
  ],
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "owner_telegram_id": "123456789"
}
```

### 2. Query User Apps
**GET** `/api/v1/user-apps/`

Query user applications with filtering options.

Query parameters:
- `telegram_id` (optional): Filter by telegram ID
- `is_active` (optional): Filter by active status
- `name_contains` (optional): Filter by name containing text
- `skip` (optional, default=0): Number of items to skip
- `limit` (optional, default=10): Number of items to return (max 100)

Example:
```
GET /api/v1/user-apps/?telegram_id=123456789&is_active=true&limit=20
```

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker

The backend is configured to run in Docker. See the main docker-compose.yml file in the project root. 