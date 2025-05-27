from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.core.database import db
from app.services.gemini_service import gemini_service
from app.utils.file_manager import file_manager
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)


class CallbackHandlers:
    """Handles inline keyboard callbacks"""
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback router"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = query.from_user
        user_data = await db.get_or_create_user(user.id, user.username)
        
        # Route to appropriate handler
        if data.startswith("cmd_"):
            await self._handle_command_callback(query, user_data["id"], data)
        elif data.startswith("research_"):
            await self._handle_research_callback(query, user_data["id"], data)
        elif data.startswith("analyze_"):
            await self._handle_analyze_callback(query, user_data["id"], data)
        elif data.startswith("createapp_"):
            await self._handle_createapp_callback(query, user_data["id"], data)
        elif data.startswith("style_"):
            await self._handle_style_callback(query, user_data["id"], data)
        elif data.startswith("interaction_"):
            await self._handle_interaction_callback(query, user_data["id"], data)
    
    async def _handle_command_callback(self, query, user_id: int, data: str):
        """Handle command selection callbacks"""
        if data == "cmd_research":
            await query.edit_message_text(
                "🔍 What fascinating subject shall we explore today?\n\nPlease type your topic:"
            )
            await db.update_user_state(
                user_id,
                current_command="research",
                state_data={"stage": "waiting_topic"}
            )
        
        elif data == "cmd_analyze":
            await query.edit_message_text(
                "🧐 Ready to analyze! Send me:\n"
                "• Text message\n"
                "• Voice message 🎤\n"
                "• Audio file 🎵\n\n"
                "(Max audio length: 5 minutes for MVP)"
            )
            await db.update_user_state(
                user_id,
                current_command="analyze",
                state_data={"stage": "waiting_content"}
            )
        
        elif data == "cmd_createapp":
            await query.edit_message_text(
                "🎨 Let's create an interactive showcase!\n\nPlease provide the content for your app:"
            )
            await db.update_user_state(
                user_id,
                current_command="createapp",
                state_data={"stage": "waiting_content"}
            )
    
    async def _handle_research_callback(self, query, user_id: int, data: str):
        """Handle research-related callbacks"""
        state = await db.get_user_state(user_id)
        state_data = json.loads(state["state_data"]) if state and state["state_data"] else {}
        
        if data == "research_suggest_refinements":
            topic = state_data.get("topic", "")
            
            # Get AI suggestions
            processing_msg = await query.message.reply_text("✨ Getting AI suggestions...")
            suggestions = await gemini_service.suggest_refinements(topic)
            await processing_msg.delete()
            
            # Create buttons for suggestions
            keyboard = []
            for i, suggestion in enumerate(suggestions[:7]):
                keyboard.append([InlineKeyboardButton(suggestion, callback_data=f"refine_{i}")])
            keyboard.append([InlineKeyboardButton("✅ Done Selecting", callback_data="research_start")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🔍 Researching: *{topic}*\n\n"
                "Select focus areas (tap to toggle):",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Update state with suggestions
            state_data["suggestions"] = suggestions
            state_data["selected_refinements"] = []
            await db.update_user_state(user_id, state_data=state_data)
        
        elif data == "research_custom_refinements":
            await query.edit_message_text(
                "✏️ Please type your specific focus areas or keywords:"
            )
            state_data["stage"] = "waiting_custom_refinements"
            await db.update_user_state(user_id, state_data=state_data)
        
        elif data == "research_to_createapp":
            # Chain to create app
            last_command = await db.get_last_command(user_id, "research")
            if last_command:
                await self._start_createapp_flow(query, user_id, last_command["output_data"])
        
        elif data == "research_start":
            # Start research with selected refinements
            topic = state_data.get("topic", "")
            refinements = state_data.get("selected_refinements", [])
            
            # Delegate to the research performer
            from app.handlers.commands import command_handlers
            await command_handlers._perform_research(
                query,
                user_id,
                topic,
                refinements
            )
    
    async def _handle_createapp_callback(self, query, user_id: int, data: str):
        """Handle create app callbacks"""
        if data == "createapp_use_research":
            last_research = await db.get_last_command(user_id, "research")
            if last_research:
                await self._start_createapp_flow(query, user_id, last_research["output_data"])
        
        elif data == "createapp_use_analysis":
            last_analysis = await db.get_last_command(user_id, "analyze")
            if last_analysis:
                await self._start_createapp_flow(query, user_id, last_analysis["output_data"])
        
        elif data == "createapp_new_content":
            await query.edit_message_text(
                "🎨 Please provide the content for your app:"
            )
            await db.update_user_state(
                user_id,
                current_command="createapp",
                state_data={"stage": "waiting_content"}
            )
    
    async def _start_createapp_flow(self, query, user_id: int, content_data: dict):
        """Start the app creation flow with content"""
        # Store content in state
        await db.update_user_state(
            user_id,
            current_command="createapp",
            state_data={
                "stage": "select_style",
                "content": content_data
            }
        )
        
        # Show style selection
        keyboard = [
            [InlineKeyboardButton("🔴 Crimson Codex", callback_data="style_crimson")],
            [InlineKeyboardButton("🌌 Quantum Void", callback_data="style_quantum")],
            [InlineKeyboardButton("🌿 Nature's Wisdom", callback_data="style_nature")],
            [InlineKeyboardButton("💜 Neon Dreams", callback_data="style_neon")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎨 Choose a visual style for your showcase:",
            reply_markup=reply_markup
        )
    
    async def _handle_style_callback(self, query, user_id: int, data: str):
        """Handle style selection"""
        style_map = {
            "style_crimson": "Crimson Codex",
            "style_quantum": "Quantum Void",
            "style_nature": "Nature's Wisdom",
            "style_neon": "Neon Dreams"
        }
        
        selected_style = style_map.get(data, "Quantum Void")
        
        # Update state
        state = await db.get_user_state(user_id)
        state_data = json.loads(state["state_data"]) if state and state["state_data"] else {}
        state_data["style"] = selected_style
        state_data["stage"] = "select_interactions"
        state_data["interactions"] = []
        
        await db.update_user_state(user_id, state_data=state_data)
        
        # Show interaction options
        keyboard = [
            [InlineKeyboardButton("✅ Interactive Quizzes", callback_data="interaction_quiz")],
            [InlineKeyboardButton("📊 Data Charts", callback_data="interaction_charts")],
            [InlineKeyboardButton("🎯 Progress Tracking", callback_data="interaction_progress")],
            [InlineKeyboardButton("🎮 Gamification", callback_data="interaction_game")],
            [InlineKeyboardButton("➡️ Done Configuring", callback_data="interaction_done")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✨ Style selected: *{selected_style}*\n\n"
            "Choose interaction features (tap to toggle):",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def _handle_interaction_callback(self, query, user_id: int, data: str):
        """Handle interaction feature selection"""
        state = await db.get_user_state(user_id)
        state_data = json.loads(state["state_data"]) if state and state["state_data"] else {}
        
        if data == "interaction_done":
            # Generate the app
            await self._generate_app(query, user_id, state_data)
        else:
            # Toggle interaction feature
            feature_map = {
                "interaction_quiz": "Interactive Quizzes",
                "interaction_charts": "Data Charts",
                "interaction_progress": "Progress Tracking",
                "interaction_game": "Gamification"
            }
            
            feature = feature_map.get(data)
            if feature:
                interactions = state_data.get("interactions", [])
                if feature in interactions:
                    interactions.remove(feature)
                else:
                    interactions.append(feature)
                
                state_data["interactions"] = interactions
                await db.update_user_state(user_id, state_data=state_data)
                
                # Update button text to show selection
                await query.answer(f"{'Added' if feature in interactions else 'Removed'}: {feature}")
    
    async def _generate_app(self, query, user_id: int, state_data: dict):
        """Generate the final app"""
        try:
            # Show processing message
            processing_msg = await query.message.reply_text(
                "🔥 Forging your interactive showcase...\n"
                "This may take a moment..."
            )
            
            # Generate HTML with Gemini
            html_content = await gemini_service.generate_app_html(
                content_data=state_data.get("content", {}),
                visual_style=state_data.get("style", "Quantum Void"),
                interaction_options=state_data.get("interactions", [])
            )
            
            # Save HTML file
            file_id, file_path = await file_manager.save_html_file(html_content, "app")
            app_url = settings.get_app_url(file_id)
            
            # Save to database
            await db.save_command(
                user_id=user_id,
                command_type="createapp",
                input_data=state_data,
                output_data={"file_id": file_id, "url": app_url},
                file_url=app_url
            )
            
            # Clear user state
            await db.update_user_state(user_id, current_command=None)
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send success message
            keyboard = [
                [InlineKeyboardButton("🌐 View Your Showcase", url=app_url)],
                [InlineKeyboardButton("🚀 Create Another", callback_data="cmd_createapp")],
                [InlineKeyboardButton("🔍 New Research", callback_data="cmd_research")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"🎉 **Your CogniCraft Showcase is ready!**\n\n"
                f"Style: {state_data.get('style')}\n"
                f"Features: {', '.join(state_data.get('interactions', [])) or 'Basic'}\n\n"
                f"View it online: {app_url}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Also send as file
            with open(file_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"cognicraft_{file_id}.html",
                    caption="📎 Here's your showcase as a downloadable file!"
                )
            
        except Exception as e:
            logger.error(f"Error generating app: {str(e)}")
            await query.message.reply_text(
                "❌ Sorry, I encountered an error while creating your app. Please try again."
            )


callback_handlers = CallbackHandlers()