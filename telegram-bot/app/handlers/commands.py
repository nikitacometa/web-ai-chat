from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.core.database import db
from app.services.gemini_service import gemini_service
from app.utils.file_manager import file_manager
from app.core.config import settings
import logging
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Handles all bot commands"""
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        await db.get_or_create_user(user.id, user.username)
        
        welcome_message = """🧠✨ Welcome to CogniCraft AI!

I'm your AI-powered assistant for research, analysis, and creating beautiful interactive web apps.

Here's what I can do:
🔍 /research - Deep dive into any topic
🧐 /analyze - Analyze text or audio content
🎨 /createapp - Transform content into interactive web apps

Commands can be chained! For example:
Research → Create App
Analyze → Research → Create App

Let's start creating something amazing! Which command would you like to try first?"""
        
        keyboard = [
            [InlineKeyboardButton("🔍 Research Topic", callback_data="cmd_research")],
            [InlineKeyboardButton("🧐 Analyze Content", callback_data="cmd_analyze")],
            [InlineKeyboardButton("🎨 Create App", callback_data="cmd_createapp")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def research(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /research command"""
        user = update.effective_user
        user_data = await db.get_or_create_user(user.id, user.username)
        
        # Check if topic was provided
        topic = " ".join(context.args) if context.args else None
        
        if topic:
            # Store topic in user state
            await db.update_user_state(
                user_data["id"],
                current_command="research",
                state_data={"topic": topic, "stage": "confirm"}
            )
            
            # Ask for refinements
            keyboard = [
                [InlineKeyboardButton("✨ Yes, Suggest!", callback_data="research_suggest_refinements")],
                [InlineKeyboardButton("✏️ No, I'll specify", callback_data="research_custom_refinements")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🔍 Great! I'll research: *{topic}*\n\nWould you like me to suggest some specific areas to focus on?",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("🔍 What fascinating subject shall we explore today?\n\nPlease type your topic:")
            await db.update_user_state(
                user_data["id"],
                current_command="research",
                state_data={"stage": "waiting_topic"}
            )
    
    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        user = update.effective_user
        user_data = await db.get_or_create_user(user.id, user.username)
        
        # Check if text was provided
        text = " ".join(context.args) if context.args else None
        
        if text:
            # Analyze the text directly
            await self._perform_analysis(update, user_data["id"], text, "text")
        else:
            await update.message.reply_text(
                "🧐 Ready to analyze! Send me:\n"
                "• Text message\n"
                "• Voice message 🎤\n"
                "• Audio file 🎵\n\n"
                "(Max audio length: 5 minutes for MVP)"
            )
            await db.update_user_state(
                user_data["id"],
                current_command="analyze",
                state_data={"stage": "waiting_content"}
            )
    
    async def createapp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /createapp command"""
        user = update.effective_user
        user_data = await db.get_or_create_user(user.id, user.username)
        
        # Check if we have recent research or analysis to use
        last_research = await db.get_last_command(user_data["id"], "research")
        last_analysis = await db.get_last_command(user_data["id"], "analyze")
        
        if last_research or last_analysis:
            # Offer to use recent data
            keyboard = []
            if last_research:
                keyboard.append([InlineKeyboardButton("📚 Use Recent Research", callback_data="createapp_use_research")])
            if last_analysis:
                keyboard.append([InlineKeyboardButton("🔍 Use Recent Analysis", callback_data="createapp_use_analysis")])
            keyboard.append([InlineKeyboardButton("✍️ Provide New Content", callback_data="createapp_new_content")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🎨 Let's create an interactive showcase!\n\nWould you like to use your recent work or provide new content?",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "🎨 Let's create an interactive showcase!\n\nPlease provide the content for your app:"
            )
            await db.update_user_state(
                user_data["id"],
                current_command="createapp",
                state_data={"stage": "waiting_content"}
            )
    
    async def _perform_analysis(self, update: Update, user_id: int, content: str, content_type: str):
        """Perform content analysis"""
        try:
            # Show processing message
            processing_msg = await update.message.reply_text("🧠 Analyzing content... Please wait...")
            
            # Analyze with Gemini
            analysis_result = await gemini_service.analyze_content(content, content_type)
            
            # Save to database
            command_data = await db.save_command(
                user_id=user_id,
                command_type="analyze",
                input_data={"content": content[:500], "type": content_type},  # Truncate for storage
                output_data=analysis_result
            )
            
            # Update user state
            await db.update_user_state(
                user_id=user_id,
                current_command=None,
                last_command_id=command_data["id"]
            )
            
            # Format and send results
            result_text = f"""📊 **Analysis Complete!**

**Summary:**
{analysis_result['summary']}

**Key Themes:**
• {chr(10).join('• ' + theme for theme in analysis_result['themes'])}

**Sentiment:** {analysis_result['sentiment'].title()}
**Tone:** {analysis_result['tone'].title()}

**Key Points:**
{chr(10).join(f"{i+1}. {point}" for i, point in enumerate(analysis_result.get('key_points', [])))}"""
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send results with action buttons
            keyboard = [
                [InlineKeyboardButton("💡 Research This Topic", callback_data="analyze_to_research")],
                [InlineKeyboardButton("🎨 Create App", callback_data="analyze_to_createapp")],
                [InlineKeyboardButton("🚀 New Analysis", callback_data="cmd_analyze")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                result_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error during analysis. Please try again."
            )
    
    async def _perform_research(self, update: Update, user_id: int, topic: str, refinements: List[str] = None):
        """Perform topic research"""
        try:
            # Show processing message
            processing_msg = await update.message.reply_text("🔬 Conducting deep research... This may take a moment...")
            
            # Research with Gemini
            research_result = await gemini_service.research_topic(topic, refinements)
            
            # Save research HTML
            file_id, file_path = await file_manager.save_research_html(research_result, topic)
            research_url = settings.get_research_url(file_id)
            
            # Save to database
            command_data = await db.save_command(
                user_id=user_id,
                command_type="research",
                input_data={"topic": topic, "refinements": refinements},
                output_data=research_result,
                file_url=research_url
            )
            
            # Update user state
            await db.update_user_state(
                user_id=user_id,
                current_command=None,
                last_command_id=command_data["id"]
            )
            
            # Format summary
            summary_text = f"""📚 **Research Complete: {research_result['title']}**

**Summary:**
{research_result['executive_summary'][:300]}...

**Key Concepts:** {len(research_result.get('key_concepts', []))} identified
**Current Developments:** {len(research_result.get('current_developments', []))} found
**Applications:** {len(research_result.get('practical_applications', []))} discovered
**Future Trends:** {len(research_result.get('future_trends', []))} predicted

**Complexity:** {research_result.get('metadata', {}).get('complexity_level', 'intermediate').title()}"""
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send results with action buttons
            keyboard = [
                [InlineKeyboardButton("📖 View Full Research", url=research_url)],
                [InlineKeyboardButton("🎨 Create Interactive App", callback_data="research_to_createapp")],
                [InlineKeyboardButton("🔬 Analyze Further", callback_data="research_to_analyze")],
                [InlineKeyboardButton("🚀 New Research", callback_data="cmd_research")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                summary_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in research: {str(e)}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error during research. Please try again."
            )


command_handlers = CommandHandlers()