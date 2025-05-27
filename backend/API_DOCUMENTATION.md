# User Apps API Documentation

## Overview

The User Apps API allows users to create, manage, and publish HTML applications. Each app is categorized by type (research, app, image, doc) and gets a unique URL based on its type and name.

## Base URL

```
https://api.aisatisfy.me/api/v1
```

## Endpoints

### 1. Create New App

**POST** `/user-apps/`

Creates a new user application with HTML content.

**Request Body:**
```json
{
  "name": "AI Agent Research Libraries",
  "type": "research",  // Options: "research", "app", "image", "doc"
  "code": "<html>...</html>",
  "description": "Research on AI agent libraries and frameworks",
  "required_env_vars": [],
  "telegram_id": "123456789"
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "AI Agent Research Libraries",
  "type": "research",
  "code": "<html>...</html>",
  "url": "https://aisatisfy.me/research/ai_agent_research_libraries",
  "description": "Research on AI agent libraries and frameworks",
  "required_env_vars": [],
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "owner_telegram_id": "123456789"
}
```

### 2. Get User's Apps

**GET** `/user-apps/user/{telegram_id}`

Retrieves all apps owned by a specific user.

**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "name": "AI Agent Research Libraries",
    "type": "research",
    "code": "<html>...</html>",
    "url": "https://aisatisfy.me/research/ai_agent_research_libraries",
    "description": "Research on AI agent libraries and frameworks",
    "required_env_vars": [],
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "owner_telegram_id": "123456789"
  }
]
```

### 3. Update App

**PUT** `/user-apps/{app_id}`

Updates an existing user application.

**Request Body:**
```json
{
  "name": "Updated App Name",        // Optional
  "type": "app",                     // Optional
  "code": "<html>Updated...</html>", // Optional
  "description": "Updated description", // Optional
  "required_env_vars": [],           // Optional
  "is_active": false                 // Optional
}
```

**Response:** Same as create response with updated fields.

### 4. Query Apps

**GET** `/user-apps/`

Query apps with various filters.

**Query Parameters:**
- `telegram_id`: Filter by owner's telegram ID
- `type`: Filter by app type (research, app, image, doc)
- `is_active`: Filter by active status (true/false)
- `name_contains`: Filter by name containing text
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 10, max: 100)

### 5. Delete App

**DELETE** `/user-apps/{app_id}`

Deletes a user application and its associated HTML file.

**Response:**
```json
{
  "message": "App deleted successfully"
}
```

## App Types and URL Structure

Apps are categorized into four types, each with its own URL structure:

1. **Research**: `https://aisatisfy.me/research/{app_name}`
   - For research papers, analysis, and academic content

2. **App**: `https://aisatisfy.me/app/{app_name}`
   - For interactive applications and tools

3. **Image**: `https://aisatisfy.me/image/{app_name}`
   - For image galleries and visualizations

4. **Doc**: `https://aisatisfy.me/doc/{app_name}`
   - For documents, reports, and written content

## File Storage

- HTML files are stored in `/var/www/api-files/`
- Files are named using a sanitized version of the app name
- Special characters are removed and spaces are replaced with underscores

## Example Usage

### Creating a Research App

```bash
curl -X POST https://api.aisatisfy.me/api/v1/user-apps/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Agent Libraries Research",
    "type": "research",
    "code": "<html><body><h1>Research Content</h1></body></html>",
    "description": "Comprehensive research on AI agent libraries",
    "telegram_id": "123456789"
  }'
```

### Getting All Apps for a User

```bash
curl https://api.aisatisfy.me/api/v1/user-apps/user/123456789
```

### Updating an App

```bash
curl -X PUT https://api.aisatisfy.me/api/v1/user-apps/{app_id} \
  -H "Content-Type: application/json" \
  -d '{
    "code": "<html><body><h1>Updated Content</h1></body></html>"
  }'
``` 