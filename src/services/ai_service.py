"""
AI service for the Fal Gram Bot.
Handles integrations with Gemini and DeepSeek AI APIs.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from config.settings import settings
from src.utils.logger import logger

# Optional supabase import
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase not available - database features will be limited")


class AIService:
    """AI service for handling AI integrations."""
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.rate_limit_cache = {}
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW
        self.rate_limit_requests = settings.RATE_LIMIT_REQUESTS
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit."""
        if not settings.RATE_LIMIT_ENABLED:
            return True
        
        now = datetime.now()
        user_cache = self.rate_limit_cache.get(user_id, [])
        
        # Remove old requests outside the window
        user_cache = [req_time for req_time in user_cache 
                     if now - req_time < timedelta(seconds=self.rate_limit_window)]
        
        # Check if user has exceeded limit
        if len(user_cache) >= self.rate_limit_requests:
            return False
        
        # Add current request
        user_cache.append(now)
        self.rate_limit_cache[user_id] = user_cache
        
        return True
    
    async def _make_gemini_request(self, prompt: str, image_data: Optional[bytes] = None, model: Optional[str] = None) -> Optional[str]:
        """Make request to Gemini API with optional model override."""
        if not self.gemini_api_key:
            logger.warning("Gemini API key not configured")
            return None
        
        try:
            # Determine model
            if not model:
                model = "gemini-pro-vision" if image_data else "gemini-pro"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.gemini_api_key
            }
            
            # Prepare content
            content = [{"text": prompt}]
            if image_data:
                import base64
                image_b64 = base64.b64encode(image_data).decode('utf-8')
                content = [
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": image_b64
                        }
                    },
                    {"text": prompt}
                ]
            
            payload = {
                "contents": [{"parts": content}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'candidates' in data and data['candidates']:
                            return data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        logger.error(f"Gemini API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error making Gemini request: {e}")
            return None

    async def generate_with_fallback(self, user_id: int, prompt: str, image_data: Optional[bytes] = None) -> Optional[str]:
        """Generate text using provider fallback: Gemini 2.5 Flash Lite -> 2.0 Flash -> DeepSeek -> Gemini 1.5 -> legacy.
        Does rate limiting per user.
        """
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."

        # Preferred Gemini model order
        gemini_models = [
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
        ]
        for model in gemini_models:
            result = await self._make_gemini_request(prompt, image_data=image_data, model=model)
            if result:
                return result

        # DeepSeek as fallback (text only)
        ds_prompt = prompt if not image_data else prompt + "\n\n(Visual reference provided; describe based on text instructions as needed.)"
        result = await self._make_deepseek_request(ds_prompt)
        if result:
            return result

        # Gemini legacy last chance
        result = await self._make_gemini_request(prompt, image_data=image_data, model=None)
        return result
    
    async def _make_deepseek_request(self, prompt: str) -> Optional[str]:
        """Make request to DeepSeek API."""
        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not configured")
            return None
        
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a mystical fortune teller and astrologer. Provide insightful, positive, and helpful interpretations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'choices' in data and data['choices']:
                            return data['choices'][0]['message']['content']
                    else:
                        logger.error(f"DeepSeek API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error making DeepSeek request: {e}")
            return None
    
    async def generate_coffee_fortune(self, user_id: int, image_data: bytes) -> Optional[str]:
        """Generate coffee fortune from image."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        
        prompt = """You are an expert coffee fortune teller. Analyze this coffee cup image and provide a detailed, mystical interpretation.

Include:
1. General energy and mood
2. Love and relationships
3. Career and opportunities
4. Health and well-being
5. A positive message for the future

Make it mystical, positive, and inspiring. Write in a warm, caring tone."""

        # Try Gemini first (better for image analysis)
        result = await self._make_gemini_request(prompt, image_data)
        if result:
            return result
        
        # Fallback to DeepSeek (text only)
        result = await self._make_deepseek_request(prompt + "\n\nNote: I cannot see the image, so I'll provide a general coffee fortune reading.")
        return result
    
    async def generate_tarot_interpretation(self, user_id: int, card: str) -> Optional[str]:
        """Generate tarot card interpretation."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        
        prompt = f"""You are an expert tarot reader. Provide a detailed interpretation of the {card} card.

Include:
1. Card meaning and symbolism
2. What this card reveals about the querent's situation
3. Guidance and advice
4. Positive aspects and opportunities
5. A message of hope and encouragement

Make it mystical, insightful, and uplifting. Write in a caring, supportive tone."""

        # Try DeepSeek first (better for text generation)
        result = await self._make_deepseek_request(prompt)
        if result:
            return result
        
        # Fallback to Gemini
        result = await self._make_gemini_request(prompt)
        return result
    
    async def generate_tarot_spread_interpretation(self, user_id: int, cards: List[Dict[str, Any]]) -> Optional[str]:
        """Generate interpretation for a spread of tarot cards using both names and meanings."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        try:
            card_names = ", ".join(card.get("name", "") for card in cards)
            card_meanings = "; ".join(card.get("meaning", "") for card in cards)
            prompt = (
                "You are an expert tarot reader. Provide a cohesive interpretation for the following spread.\n\n"
                f"Cards: {card_names}\n"
                f"Card meanin gs (provided as hints): {card_meanings}\n\n"
                "Include: overall theme, present situation, guidance, and a hopeful message."
            )
            # Prefer DeepSeek for text
            result = await self._make_deepseek_request(prompt)
            if result:
                return result
            return await self._make_gemini_request(prompt)
        except Exception as e:
            logger.error(f"Error generating spread interpretation: {e}")
            return None
    
    async def generate_dream_interpretation(self, user_id: int, dream_text: str) -> Optional[str]:
        """Generate dream interpretation."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        
        prompt = f"""You are an expert dream interpreter. Analyze this dream and provide a detailed interpretation.

Dream: {dream_text}

Include:
1. Symbolic meanings of key elements
2. Emotional and psychological insights
3. What the dream reveals about the dreamer's subconscious
4. Guidance and messages from the unconscious
5. Positive interpretations and growth opportunities

Make it insightful, supportive, and encouraging. Focus on personal growth and understanding."""

        # Try DeepSeek first
        result = await self._make_deepseek_request(prompt)
        if result:
            return result
        
        # Fallback to Gemini
        result = await self._make_gemini_request(prompt)
        return result
    
    async def generate_horoscope(self, user_id: int, sign: str, period: str = "daily") -> Optional[str]:
        """Generate horoscope for zodiac sign."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        
        prompt = f"""You are an expert astrologer. Create a detailed {period} horoscope for {sign} sign.

Include:
1. General energy and atmosphere for {sign}
2. Love and relationships guidance
3. Career and financial insights
4. Health and wellness advice
5. Lucky elements and positive affirmations

Make it personalized, positive, and inspiring. Write in a warm, encouraging tone that resonates with {sign} characteristics."""

        # Try DeepSeek first
        result = await self._make_deepseek_request(prompt)
        if result:
            return result
        
        # Fallback to Gemini
        result = await self._make_gemini_request(prompt)
        return result
    
    async def generate_compatibility_analysis(self, user_id: int, sign1: str, sign2: str) -> Optional[str]:
        """Generate compatibility analysis between two signs."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        
        prompt = f"""You are an expert astrologer. Analyze the compatibility between {sign1} and {sign2} signs.

Include:
1. Overall compatibility percentage and rating
2. Love and romantic compatibility
3. Communication styles and harmony
4. Strengths of this combination
5. Areas that may need attention
6. Tips for enhancing the relationship

Make it balanced, insightful, and constructive. Focus on understanding and growth opportunities."""

        # Try DeepSeek first
        result = await self._make_deepseek_request(prompt)
        if result:
            return result
        
        # Fallback to Gemini
        result = await self._make_gemini_request(prompt)
        return result
    
    async def generate_birth_chart_analysis(self, user_id: int, sign: str, birth_info: str) -> Optional[str]:
        """Generate birth chart analysis."""
        if not self._check_rate_limit(user_id):
            return "Rate limit exceeded. Please try again later."
        
        prompt = f"""You are an expert astrologer. Create a detailed birth chart analysis for {sign} sign.

Birth Information: {birth_info}

Include:
1. Sun sign characteristics and personality traits
2. Rising sign (Ascendant) influences
3. Moon sign emotional nature
4. Key planetary placements and their effects
5. Life areas: career, love, health, spirituality
6. Personal strengths and growth opportunities

Make it comprehensive, personalized, and inspiring. Write in a warm, supportive tone."""

        # Try DeepSeek first
        result = await self._make_deepseek_request(prompt)
        if result:
            return result
        
        # Fallback to Gemini
        result = await self._make_gemini_request(prompt)
        return result


# Global AI service instance
ai_service = AIService() 