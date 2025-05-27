from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.core.config import settings
from app.handlers.commands import command_handlers
from app.handlers.callbacks import callback_handlers
from app.handlers.messages import message_handlers
import logging
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="CogniCraft AI Bot")

# Create Telegram application
telegram_app = None


@app.on_event("startup")
async def startup_event():
    """Initialize Telegram bot on startup"""
    global telegram_app
    
    # Initialize Telegram bot
    telegram_app = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    telegram_app.add_handler(CommandHandler("start", command_handlers.start))
    telegram_app.add_handler(CommandHandler("research", command_handlers.research))
    telegram_app.add_handler(CommandHandler("analyze", command_handlers.analyze))
    telegram_app.add_handler(CommandHandler("createapp", command_handlers.createapp))
    
    # Add callback query handler
    telegram_app.add_handler(CallbackQueryHandler(callback_handlers.handle_callback))
    
    # Add message handlers
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.handle_text_message))
    telegram_app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, message_handlers.handle_audio_message))
    
    # Initialize the application
    await telegram_app.initialize()
    await telegram_app.start()
    
    # Set webhook if configured
    if settings.webhook_url:
        await telegram_app.bot.set_webhook(f"{settings.webhook_url}/webhook")
        logger.info(f"Webhook set to: {settings.webhook_url}/webhook")
    else:
        # Start polling for development
        await telegram_app.updater.start_polling()
        logger.info("Bot started in polling mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global telegram_app
    if telegram_app:
        await telegram_app.stop()
        await telegram_app.shutdown()


@app.post("/webhook")
async def webhook(request: Request):
    """Handle Telegram webhook"""
    if not telegram_app:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    
    # Process update
    await telegram_app.process_update(update)
    
    return {"ok": True}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CogniCraft AI Bot",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Serve generated files (for development/testing)
if settings.debug:
    @app.get("/with-research/{file_id}")
    async def serve_research(file_id: str):
        """Serve research HTML files"""
        file_path = os.path.join(settings.research_dir, f"{file_id}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="Research not found")
    
    @app.get("/with-app/{file_id}")
    async def serve_app(file_id: str):
        """Serve app HTML files"""
        file_path = os.path.join(settings.apps_dir, f"{file_id}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="App not found")
    
    # Simple test UI for development
    @app.get("/test-ui", response_class=HTMLResponse)
    async def test_ui():
        """Simple test UI for development"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>CogniCraft AI - Test UI</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">CogniCraft AI Test Interface</h1>
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">Test Create App</h2>
            <form id="createAppForm">
                <textarea id="content" class="w-full p-3 border rounded mb-4" rows="6" 
                    placeholder="Enter content for your app..."></textarea>
                
                <select id="style" class="w-full p-3 border rounded mb-4">
                    <option value="Crimson Codex">Crimson Codex</option>
                    <option value="Quantum Void">Quantum Void</option>
                    <option value="Nature's Wisdom">Nature's Wisdom</option>
                    <option value="Neon Dreams">Neon Dreams</option>
                </select>
                
                <div class="mb-4">
                    <label class="block mb-2">Interaction Options:</label>
                    <label class="flex items-center mb-2">
                        <input type="checkbox" value="Interactive Quizzes" class="mr-2">
                        Interactive Quizzes
                    </label>
                    <label class="flex items-center mb-2">
                        <input type="checkbox" value="Data Charts" class="mr-2">
                        Data Charts
                    </label>
                    <label class="flex items-center mb-2">
                        <input type="checkbox" value="Progress Tracking" class="mr-2">
                        Progress Tracking
                    </label>
                </div>
                
                <button type="submit" class="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-600">
                    Generate App
                </button>
            </form>
        </div>
        
        <div id="result" class="bg-white rounded-lg shadow-md p-6 hidden">
            <h3 class="text-lg font-semibold mb-4">Result:</h3>
            <div id="resultContent"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('createAppForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const content = document.getElementById('content').value;
            const style = document.getElementById('style').value;
            const interactions = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                .map(cb => cb.value);
            
            const resultDiv = document.getElementById('result');
            const resultContent = document.getElementById('resultContent');
            
            resultDiv.classList.remove('hidden');
            resultContent.innerHTML = '<p>Generating app...</p>';
            
            try {
                const response = await fetch('/api/test/create-app', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        content: {title: 'Test App', main_content: content},
                        visual_style: style,
                        interaction_options: interactions
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultContent.innerHTML = `
                        <p class="text-green-600 mb-2">App generated successfully!</p>
                        <p>URL: <a href="${data.url}" target="_blank" class="text-blue-500 underline">${data.url}</a></p>
                        <textarea class="w-full mt-4 p-3 border rounded" rows="10">${data.html}</textarea>
                    `;
                } else {
                    resultContent.innerHTML = `<p class="text-red-600">Error: ${data.error}</p>`;
                }
            } catch (error) {
                resultContent.innerHTML = `<p class="text-red-600">Error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
"""
    
    @app.post("/api/test/create-app")
    async def test_create_app(request: Request):
        """Test endpoint for app creation"""
        try:
            data = await request.json()
            
            # Generate HTML using Gemini
            from app.services.gemini_service import gemini_service
            from app.utils.file_manager import file_manager
            
            html_content = await gemini_service.generate_app_html(
                content_data=data["content"],
                visual_style=data["visual_style"],
                interaction_options=data["interaction_options"]
            )
            
            # Save file
            file_id, file_path = await file_manager.save_html_file(html_content, "app")
            app_url = f"/with-app/{file_id}"
            
            return {
                "success": True,
                "url": app_url,
                "file_id": file_id,
                "html": html_content[:1000] + "..." if len(html_content) > 1000 else html_content
            }
        except Exception as e:
            logger.error(f"Test create app error: {str(e)}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )