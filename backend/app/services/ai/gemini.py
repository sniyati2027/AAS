from typing import Optional, List, Dict, Any
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

from app.core.config import settings


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.ai_model)
        else:
            self.model = None

    def is_available(self) -> bool:
        """Check if Gemini API is configured."""
        return self.model is not None

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Gemini."""
        if not self.is_available():
            raise ValueError("Gemini API key not configured")

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=2048,
        )

        if system_instruction:
            model = genai.GenerativeModel(
                settings.ai_model,
                system_instruction=system_instruction,
            )
        else:
            model = self.model

        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config,
        )
        return response.text

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Chat with Gemini, optionally with function calling."""
        if not self.is_available():
            raise ValueError("Gemini API key not configured")

        model_config = {"model_name": settings.ai_model}
        
        if system_instruction:
            model_config["system_instruction"] = system_instruction
            
        if tools:
            model_config["tools"] = tools

        model = genai.GenerativeModel(**model_config)
        chat = model.start_chat()

        for msg in messages[:-1]:
            await chat.send_message_async(msg["content"])

        response = await chat.send_message_async(messages[-1]["content"])
        
        result = {
            "content": response.text if response.text else "",
            "function_calls": [],
        }

        if hasattr(response, "candidates") and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call"):
                    result["function_calls"].append({
                        "name": part.function_call.name,
                        "args": dict(part.function_call.args),
                    })

        return result


gemini_client = GeminiClient()
