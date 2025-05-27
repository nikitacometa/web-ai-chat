#!/usr/bin/env python3
"""
Health check script for CogniCraft AI Bot
Tests configuration and basic functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment configuration...\n")
    
    errors = []
    warnings = []
    
    # Check Telegram Bot Token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        errors.append("❌ TELEGRAM_BOT_TOKEN is not set")
    elif bot_token == "placeholder_bot_token":
        errors.append("❌ TELEGRAM_BOT_TOKEN is still using placeholder value")
    else:
        print("✅ TELEGRAM_BOT_TOKEN is configured")
    
    # Check Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        errors.append("❌ GEMINI_API_KEY is not set")
    elif gemini_key == "placeholder_gemini_key":
        errors.append("❌ GEMINI_API_KEY is still using placeholder value")
    else:
        print("✅ GEMINI_API_KEY is configured")
    
    # Check optional configurations
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url or supabase_url == "placeholder_supabase_url":
        warnings.append("⚠️  SUPABASE_URL not configured (optional for MVP)")
    else:
        print("✅ SUPABASE_URL is configured")
    
    # Check directories
    apps_dir = os.getenv("APPS_DIR", "./generated_apps")
    if os.path.exists(apps_dir):
        print(f"✅ Apps directory exists: {apps_dir}")
    else:
        print(f"📁 Apps directory will be created: {apps_dir}")
    
    # Print results
    print("\n" + "="*50)
    
    if errors:
        print("\n🚨 ERRORS FOUND:")
        for error in errors:
            print(f"   {error}")
        print("\nTo fix these errors:")
        print("1. Get a bot token from @BotFather on Telegram")
        print("2. Get a Gemini API key from https://makersuite.google.com/app/apikey")
        print("3. Update the .env file with real values")
        return False
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
    
    print("\n✅ All required configurations are set!")
    print("The bot should be able to start successfully.")
    return True

def main():
    print("🧠✨ CogniCraft AI Bot - Health Check\n")
    
    if check_environment():
        print("\n🚀 Ready to run: python mvp.py")
        sys.exit(0)
    else:
        print("\n❌ Configuration issues detected. Please fix them before running the bot.")
        sys.exit(1)

if __name__ == "__main__":
    main()