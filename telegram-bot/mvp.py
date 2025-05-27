"""
Minimal MVP for CogniCraft AI Bot
Focus: /createapp command only
"""

import os
import sys
import uuid
import logging
import httpx
import json
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APPS_DIR = os.getenv("APPS_DIR", "./generated_apps")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
DOMAIN_URL = os.getenv("DOMAIN_URL", "https://aisatisfy.me")

# Validate configuration
if not BOT_TOKEN or BOT_TOKEN == "placeholder_bot_token":
    logger.error("❌ TELEGRAM_BOT_TOKEN not configured properly!")
    logger.error("Please set a valid bot token from @BotFather in the .env file")
    sys.exit(1)

if not GEMINI_API_KEY or GEMINI_API_KEY == "placeholder_gemini_key":
    logger.error("❌ GEMINI_API_KEY not configured properly!")
    logger.error("Please set a valid Gemini API key from Google AI Studio in the .env file")
    sys.exit(1)

# Create apps directory
os.makedirs(APPS_DIR, exist_ok=True)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# User states (in-memory for MVP)
user_states: Dict[int, Dict[str, Any]] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """🧠✨ Welcome to CogniCraft AI MVP!

I can transform your ideas into beautiful interactive web apps.

Use /createapp to start creating!"""
    
    await update.message.reply_text(welcome_message)


async def createapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /createapp command"""
    user_id = update.effective_user.id
    
    # Initialize user state
    user_states[user_id] = {"stage": "waiting_content"}
    
    await update.message.reply_text(
        "🎨 Let's create an interactive showcase!\n\n"
        "Please send me the content for your app:"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    
    if user_id not in user_states:
        await update.message.reply_text("Please use /createapp to start")
        return
    
    state = user_states[user_id]
    
    if state["stage"] == "waiting_content":
        # Store content and ask for style
        state["content"] = update.message.text
        state["stage"] = "select_style"
        
        keyboard = [
            [InlineKeyboardButton("🔴 Crimson Codex", callback_data="style_crimson")],
            [InlineKeyboardButton("🌌 Quantum Void", callback_data="style_quantum")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎨 Choose a visual style:",
            reply_markup=reply_markup
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_states:
        await query.edit_message_text("Session expired. Please use /createapp to start again.")
        return
    
    state = user_states[user_id]
    
    if data.startswith("style_"):
        # Store style and generate app
        style_map = {
            "style_crimson": "Crimson Codex - dark theme with red accents",
            "style_quantum": "Quantum Void - space theme with purple gradients"
        }
        
        state["style"] = style_map.get(data, "Quantum Void")
        
        await query.edit_message_text("🔥 Generating your app... This may take a moment...")
        
        try:
            # Generate HTML with Gemini
            html = await generate_html(state["content"], state["style"])
            
            # Send to backend API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/api/v1/content/app",
                    json={
                        "content": html,
                        "metadata": {
                            "style": state["style"],
                            "telegram_user": query.from_user.username or str(query.from_user.id)
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    app_id = result["id"]
                    app_url = result["url"]
                    
                    # Send success message with URL
                    await query.message.reply_text(
                        f"🎉 **Your app is ready!**\n\n"
                        f"🌐 View online: {app_url}\n\n"
                        f"Style: {state['style'].split(' - ')[0]}",
                        parse_mode="Markdown"
                    )
                    
                    # Also save locally and send as file
                    file_path = os.path.join(APPS_DIR, f"{app_id}.html")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    
                    with open(file_path, 'rb') as f:
                        await query.message.reply_document(
                            document=f,
                            filename=f"cognicraft_{app_id}.html",
                            caption=f"📎 Your app is also available at: {app_url}"
                        )
                else:
                    raise Exception(f"Backend error: {response.status_code}")
            
            # Clear user state
            del user_states[user_id]
            
        except Exception as e:
            logger.error(f"Error generating app: {str(e)}")
            await query.message.reply_text(
                "❌ Sorry, I encountered an error. Please try again with /createapp"
            )
            del user_states[user_id]


async def generate_html(content: str, style: str) -> str:
    """Generate HTML using Gemini"""
    prompt = f"""Create a single-file HTML application with this content and style:

CONTENT: {content}

STYLE: {style}

Requirements:
1. Single HTML file with embedded CSS and JavaScript
2. Use Tailwind CSS CDN
3. Fully responsive design
4. Apply the specified visual style
5. Make it interactive and engaging
6. Add smooth animations

Generate only the HTML code:"""

    response = await model.generate_content_async(prompt)
    return response.text.strip()


def main():
    """Run the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("createapp", createapp))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start bot
    logger.info("Starting CogniCraft AI MVP Bot...")
    application.run_polling()


if __name__ == "__main__":
    main()