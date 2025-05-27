import google.generativeai as genai
from app.core.config import settings
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    async def generate_app_html(
        self,
        content_data: Dict[str, Any],
        visual_style: str,
        interaction_options: List[str]
    ) -> str:
        """Generate interactive HTML app from content"""
        
        prompt = f"""Create a single-file interactive HTML application based on the following content and requirements:

CONTENT DATA:
{json.dumps(content_data, indent=2)}

VISUAL STYLE: {visual_style}
INTERACTION OPTIONS: {', '.join(interaction_options)}

Requirements:
1. Create a complete, single HTML file with embedded CSS and JavaScript
2. Use Tailwind CSS via CDN for styling
3. Implement the visual style "{visual_style}" with appropriate colors, fonts, and design
4. Make it fully responsive for all devices
5. Include the requested interaction options: {interaction_options}
6. Use modern, clean design principles
7. Ensure all content is properly displayed and interactive
8. Add smooth animations and transitions

Visual Style Guidelines:
- Crimson Codex: Dark theme with crimson accents, tech-focused, monospace fonts
- Quantum Void: Deep space theme with purple/blue gradients, futuristic
- Nature's Wisdom: Earth tones, organic shapes, serif fonts
- Neon Dreams: Cyberpunk aesthetic, bright neon colors on dark background

Generate only the HTML code, no explanations."""

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            raise
    
    async def analyze_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Analyze text or audio content"""
        
        prompt = f"""Analyze the following {content_type} content and provide a structured analysis:

CONTENT:
{content}

Provide analysis in this exact JSON format:
{{
    "summary": "A concise summary in 100 words or less",
    "themes": ["theme1", "theme2", "theme3"],
    "sentiment": "positive/negative/neutral/mixed",
    "tone": "analytical/narrative/persuasive/informative/etc",
    "key_points": ["point1", "point2", "point3"]
}}

Return only valid JSON, no other text."""

        try:
            response = await self.model.generate_content_async(prompt)
            # Clean and parse JSON response
            json_str = response.text.strip()
            # Remove markdown code blocks if present
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str.strip())
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            raise
    
    async def research_topic(self, topic: str, refinements: Optional[List[str]] = None) -> Dict[str, Any]:
        """Conduct deep research on a topic"""
        
        refinement_text = ""
        if refinements:
            refinement_text = f"\nFocus areas: {', '.join(refinements)}"
        
        prompt = f"""Conduct comprehensive research on the following topic:

TOPIC: {topic}
{refinement_text}

Provide a thorough analysis in this exact JSON format:
{{
    "title": "Research title",
    "executive_summary": "200-word executive summary",
    "key_concepts": [
        {{"concept": "name", "explanation": "detailed explanation"}}
    ],
    "current_developments": [
        {{"development": "title", "description": "details", "significance": "why it matters"}}
    ],
    "practical_applications": [
        {{"application": "name", "description": "how it works", "benefits": "advantages"}}
    ],
    "future_trends": [
        {{"trend": "name", "timeline": "when", "impact": "potential impact"}}
    ],
    "sources": [
        {{"type": "type of source", "description": "what it covers"}}
    ],
    "metadata": {{
        "research_date": "current date",
        "complexity_level": "beginner/intermediate/advanced",
        "related_topics": ["topic1", "topic2"]
    }}
}}

Ensure the research is comprehensive, accurate, and well-structured. Return only valid JSON."""

        try:
            response = await self.model.generate_content_async(prompt)
            # Clean and parse JSON response
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str.strip())
        except Exception as e:
            logger.error(f"Error researching topic: {str(e)}")
            raise
    
    async def suggest_refinements(self, topic: str) -> List[str]:
        """Suggest topic refinements"""
        
        prompt = f"""For the research topic "{topic}", suggest 5-7 specific refinements or focus areas that would make the research more valuable and targeted.

Return as a JSON array of strings, each 3-6 words long:
["refinement 1", "refinement 2", ...]

Make suggestions contextual and relevant to the topic."""

        try:
            response = await self.model.generate_content_async(prompt)
            json_str = response.text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str.strip())
        except Exception as e:
            logger.error(f"Error suggesting refinements: {str(e)}")
            return ["recent developments", "practical applications", "technical details", "future trends", "key challenges"]


gemini_service = GeminiService()