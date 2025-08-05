"""
AI service for the Fal Gram Bot.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
import google.generativeai as genai
import requests
from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("ai_service")

class AIService:
    """AI service for generating interpretations and responses."""
    
    def __init__(self):
        self.gemini_model = None
        self.rate_limiter = {}
        self.last_request_time = {}
        self.request_count = {}
        
        # Initialize Gemini
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    async def generate_astrology_interpretation(self, prompt: str, language: str = "en") -> str:
        """Generate astrology interpretation using AI."""
        try:
            # Add language context to prompt
            full_prompt = f"Generate a detailed astrology interpretation in {language} language. {prompt}"
            
            # Use Gemini if available
            if self.gemini_model:
                return await self._generate_with_gemini(full_prompt)
            
            # Fallback to DeepSeek
            return await self._generate_with_deepseek(full_prompt)
            
        except Exception as e:
            logger.error(f"Error generating astrology interpretation: {e}")
            return self._get_fallback_response("astrology", language)
    
    async def generate_fortune_interpretation(self, prompt: str, language: str = "en") -> str:
        """Generate fortune telling interpretation using AI."""
        try:
            # Add language context to prompt
            full_prompt = f"Generate a detailed fortune telling interpretation in {language} language. {prompt}"
            
            # Use Gemini if available
            if self.gemini_model:
                return await self._generate_with_gemini(full_prompt)
            
            # Fallback to DeepSeek
            return await self._generate_with_deepseek(full_prompt)
            
        except Exception as e:
            logger.error(f"Error generating fortune interpretation: {e}")
            return self._get_fallback_response("fortune", language)
    
    async def generate_image_interpretation(self, prompt: str, image_bytes: bytes, language: str = "en") -> str:
        """Generate interpretation for image using AI."""
        try:
            # Add language context to prompt
            full_prompt = f"Analyze this image and provide a detailed interpretation in {language} language. {prompt}"
            
            # Use Gemini Vision if available
            if self.gemini_model and settings.GEMINI_API_KEY:
                return await self._generate_with_gemini_vision(full_prompt, image_bytes)
            
            # Fallback to text-only interpretation
            return await self.generate_fortune_interpretation(prompt, language)
            
        except Exception as e:
            logger.error(f"Error generating image interpretation: {e}")
            return self._get_fallback_response("image", language)
    
    async def generate_chatbot_response(self, user_message: str, context: str = "", language: str = "en") -> str:
        """Generate chatbot response using AI."""
        try:
            # Create context-aware prompt
            full_prompt = f"""You are a helpful astrology and fortune telling assistant. 
            Respond in {language} language. Be friendly, mystical, and helpful.
            
            Context: {context}
            User message: {user_message}
            
            Provide a helpful and engaging response:"""
            
            # Use Gemini if available
            if self.gemini_model:
                return await self._generate_with_gemini(full_prompt)
            
            # Fallback to DeepSeek
            return await self._generate_with_deepseek(full_prompt)
            
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return self._get_fallback_response("chatbot", language)
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Gemini API."""
        try:
            # Check rate limiting
            if not self._check_rate_limit("gemini"):
                return "Rate limit exceeded. Please try again later."
            
            # Generate response
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt
            )
            
            # Update rate limiting
            self._update_rate_limit("gemini")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error with Gemini API: {e}")
            raise
    
    async def _generate_with_gemini_vision(self, prompt: str, image_bytes: bytes) -> str:
        """Generate response using Gemini Vision API."""
        try:
            # Check rate limiting
            if not self._check_rate_limit("gemini_vision"):
                return "Rate limit exceeded. Please try again later."
            
            # Create image part
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            # Generate response
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                [prompt, image_part]
            )
            
            # Update rate limiting
            self._update_rate_limit("gemini_vision")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error with Gemini Vision API: {e}")
            raise
    
    async def _generate_with_deepseek(self, prompt: str) -> str:
        """Generate response using DeepSeek API."""
        try:
            # Check rate limiting
            if not self._check_rate_limit("deepseek"):
                return "Rate limit exceeded. Please try again later."
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Make request
            response = await asyncio.to_thread(
                requests.post,
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Update rate limiting
            self._update_rate_limit("deepseek")
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Error with DeepSeek API: {e}")
            raise
    
    def _check_rate_limit(self, provider: str) -> bool:
        """Check if rate limit is exceeded."""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old entries
        if provider in self.request_count:
            self.request_count[provider] = [
                req_time for req_time in self.request_count[provider]
                if req_time > window_start
            ]
        else:
            self.request_count[provider] = []
        
        # Check limit
        max_requests = 60 if provider.startswith("gemini") else 30
        return len(self.request_count[provider]) < max_requests
    
    def _update_rate_limit(self, provider: str) -> None:
        """Update rate limiting counters."""
        current_time = time.time()
        
        if provider not in self.request_count:
            self.request_count[provider] = []
        
        self.request_count[provider].append(current_time)
        self.last_request_time[provider] = current_time
    
    def _get_fallback_response(self, response_type: str, language: str) -> str:
        """Get fallback response when AI is unavailable."""
        fallback_responses = {
            "astrology": {
                "en": "I'm sorry, I'm having trouble connecting to the stars right now. Please try again later.",
                "tr": "Üzgünüm, şu anda yıldızlarla bağlantı kurmakta sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.",
                "es": "Lo siento, estoy teniendo problemas para conectar con las estrellas en este momento. Por favor, inténtalo de nuevo más tarde."
            },
            "fortune": {
                "en": "The mystical forces are quiet right now. Please try again in a moment.",
                "tr": "Mistik güçler şu anda sessiz. Lütfen bir dakika sonra tekrar deneyin.",
                "es": "Las fuerzas místicas están calladas en este momento. Por favor, inténtalo de nuevo en un momento."
            },
            "image": {
                "en": "I'm having trouble reading the image right now. Please try again later.",
                "tr": "Şu anda resmi okumakta sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.",
                "es": "Estoy teniendo problemas para leer la imagen en este momento. Por favor, inténtalo de nuevo más tarde."
            },
            "chatbot": {
                "en": "I'm temporarily unavailable. Please try again in a few moments.",
                "tr": "Geçici olarak müsait değilim. Lütfen birkaç dakika sonra tekrar deneyin.",
                "es": "Estoy temporalmente no disponible. Por favor, inténtalo de nuevo en unos momentos."
            }
        }
        
        return fallback_responses.get(response_type, {}).get(language, fallback_responses[response_type]["en"])
    
    async def test_connection(self) -> Dict[str, bool]:
        """Test AI service connections."""
        results = {}
        
        # Test Gemini
        if settings.GEMINI_API_KEY:
            try:
                test_prompt = "Hello, this is a test message."
                await self._generate_with_gemini(test_prompt)
                results["gemini"] = True
            except Exception as e:
                logger.error(f"Gemini connection test failed: {e}")
                results["gemini"] = False
        else:
            results["gemini"] = False
        
        # Test DeepSeek
        if settings.DEEPSEEK_API_KEY:
            try:
                test_prompt = "Hello, this is a test message."
                await self._generate_with_deepseek(test_prompt)
                results["deepseek"] = True
            except Exception as e:
                logger.error(f"DeepSeek connection test failed: {e}")
                results["deepseek"] = False
        else:
            results["deepseek"] = False
        
        return results

# Global AI service instance
ai_service = AIService()