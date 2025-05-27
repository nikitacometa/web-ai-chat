from telegram import Update
from telegram.ext import ContextTypes
from app.core.database import db
from app.handlers.commands import command_handlers
from app.services.gemini_service import gemini_service
import logging
import json

logger = logging.getLogger(__name__)


class MessageHandlers:
    """Handles text, audio, and other message types"""
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages based on current user state"""
        user = update.effective_user
        user_data = await db.get_or_create_user(user.id, user.username)
        
        # Get current user state
        state = await db.get_user_state(user_data["id"])
        if not state or not state["current_command"]:
            # No active command, provide help
            await update.message.reply_text(
                "Please use one of the commands:\n"
                "🔍 /research - Deep dive into any topic\n"
                "🧐 /analyze - Analyze content\n"
                "🎨 /createapp - Create interactive app"
            )
            return
        
        state_data = json.loads(state["state_data"]) if state["state_data"] else {}
        current_command = state["current_command"]
        
        # Route based on current command and stage
        if current_command == "research":
            await self._handle_research_text(update, user_data["id"], state_data)
        elif current_command == "analyze":
            await self._handle_analyze_text(update, user_data["id"], state_data)
        elif current_command == "createapp":
            await self._handle_createapp_text(update, user_data["id"], state_data)
    
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio/voice messages"""
        user = update.effective_user
        user_data = await db.get_or_create_user(user.id, user.username)
        
        # Get current user state
        state = await db.get_user_state(user_data["id"])
        if not state or state["current_command"] != "analyze":
            await update.message.reply_text(
                "🎤 To analyze audio, please use the /analyze command first."
            )
            return
        
        # Process audio
        await update.message.reply_text("🎧 Processing your audio...")
        
        # Get audio file
        if update.message.voice:
            file = await update.message.voice.get_file()
            audio_type = "voice"
        elif update.message.audio:
            file = await update.message.audio.get_file()
            audio_type = "audio"
        else:
            await update.message.reply_text("❌ Unsupported audio format.")
            return
        
        try:
            # Download audio file
            file_path = f"/tmp/audio_{user.id}_{update.message.message_id}.ogg"
            await file.download_to_drive(file_path)
            
            # For MVP, we'll transcribe and analyze as text
            # In production, use speech-to-text service or Gemini's audio capabilities
            await update.message.reply_text(
                "🎵 Audio processing is in development. For now, please send text content."
            )
            
            # Clean up
            import os
            os.remove(file_path)
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            await update.message.reply_text(
                "❌ Error processing audio. Please try again."
            )
    
    async def _handle_research_text(self, update: Update, user_id: int, state_data: dict):
        """Handle text input during research flow"""
        stage = state_data.get("stage")
        
        if stage == "waiting_topic":
            # Store topic and ask for refinements
            topic = update.message.text.strip()
            state_data["topic"] = topic
            state_data["stage"] = "confirm"
            
            await db.update_user_state(user_id, state_data=state_data)
            
            # Ask for refinements
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("✨ Yes, Suggest!", callback_data="research_suggest_refinements")],
                [InlineKeyboardButton("✏️ No, I'll specify", callback_data="research_custom_refinements")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🔍 Great! I'll research: *{topic}*\n\n"
                "Would you like me to suggest some specific areas to focus on?",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        
        elif stage == "waiting_custom_refinements":
            # Parse custom refinements
            refinements = [r.strip() for r in update.message.text.split(",")]
            state_data["selected_refinements"] = refinements
            
            # Start research
            topic = state_data.get("topic", "")
            await command_handlers._perform_research(update, user_id, topic, refinements)
    
    async def _handle_analyze_text(self, update: Update, user_id: int, state_data: dict):
        """Handle text input during analyze flow"""
        stage = state_data.get("stage")
        
        if stage == "waiting_content":
            # Analyze the text
            await command_handlers._perform_analysis(
                update, user_id, update.message.text, "text"
            )
    
    async def _handle_createapp_text(self, update: Update, user_id: int, state_data: dict):
        """Handle text input during create app flow"""
        stage = state_data.get("stage")
        
        if stage == "waiting_content":
            # Store content and move to style selection
            content = {
                "title": "User Content",
                "main_content": update.message.text,
                "type": "text"
            }
            
            state_data["content"] = content
            state_data["stage"] = "select_style"
            
            await db.update_user_state(user_id, state_data=state_data)
            
            # Show style selection
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("🔴 Crimson Codex", callback_data="style_crimson")],
                [InlineKeyboardButton("🌌 Quantum Void", callback_data="style_quantum")],
                [InlineKeyboardButton("🌿 Nature's Wisdom", callback_data="style_nature")],
                [InlineKeyboardButton("💜 Neon Dreams", callback_data="style_neon")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🎨 Choose a visual style for your showcase:",
                reply_markup=reply_markup
            )


message_handlers = MessageHandlers()