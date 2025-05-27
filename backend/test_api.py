import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Test user telegram ID
TEST_TELEGRAM_ID = "123456789"

def test_create_app():
    """Test creating a new app"""
    print("Testing create app...")
    
    app_data = {
        "name": "AI Agent Research Libraries",
        "type": "research",
        "code": """
        <html>
        <head>
            <title>AI Agent Research Libraries</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                p { line-height: 1.6; }
            </style>
        </head>
        <body>
            <h1>Research on AI Agent Libraries</h1>
            <p>This is a comprehensive research on various AI agent libraries...</p>
        </body>
        </html>
        """,
        "description": "Research on AI agent libraries and frameworks",
        "required_env_vars": [],
        "telegram_id": TEST_TELEGRAM_ID
    }
    
    response = requests.post(f"{BASE_URL}/user-apps/", json=app_data)
    if response.status_code == 200:
        print("✅ App created successfully!")
        return response.json()
    else:
        print(f"❌ Error creating app: {response.status_code} - {response.text}")
        return None

def test_get_user_apps(telegram_id):
    """Test getting all apps for a user"""
    print(f"\nTesting get user apps for telegram_id: {telegram_id}...")
    
    response = requests.get(f"{BASE_URL}/user-apps/user/{telegram_id}")
    if response.status_code == 200:
        apps = response.json()
        print(f"✅ Found {len(apps)} apps for user")
        for app in apps:
            print(f"  - {app['name']} ({app['type']}): {app.get('url', 'No URL')}")
        return apps
    else:
        print(f"❌ Error getting apps: {response.status_code} - {response.text}")
        return []

def test_update_app(app_id):
    """Test updating an app"""
    print(f"\nTesting update app {app_id}...")
    
    update_data = {
        "description": "Updated research on AI agent libraries with new findings",
        "code": """
        <html>
        <head>
            <title>AI Agent Research Libraries - Updated</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                h2 { color: #666; }
                p { line-height: 1.6; }
            </style>
        </head>
        <body>
            <h1>Research on AI Agent Libraries</h1>
            <h2>Updated with Latest Findings</h2>
            <p>This is a comprehensive research on various AI agent libraries...</p>
            <p>New findings include comparison of LangChain, AutoGPT, and more...</p>
        </body>
        </html>
        """
    }
    
    response = requests.put(f"{BASE_URL}/user-apps/{app_id}", json=update_data)
    if response.status_code == 200:
        print("✅ App updated successfully!")
        updated_app = response.json()
        print(f"  URL: {updated_app.get('url', 'No URL')}")
        return updated_app
    else:
        print(f"❌ Error updating app: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("Starting API tests...\n")
    
    # Create a new app
    created_app = test_create_app()
    
    if created_app:
        app_id = created_app["id"]
        
        # Get all user apps
        test_get_user_apps(TEST_TELEGRAM_ID)
        
        # Update the app
        test_update_app(app_id)
        
        # Get all user apps again to see the changes
        test_get_user_apps(TEST_TELEGRAM_ID)
    
    print("\nTests completed!") 