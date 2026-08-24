import os
import google.generativeai as genai
from .base import BaseLLMProvider

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, model: str = "gemini-1.5-pro"):
        self.model = model
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        # Gemini system prompt is usually set in model initialization, 
        # but we can simulate it by prepending it for simplicity.
        full_prompt = f"System Instructions:\n{system_prompt}\n\nUser Request:\n{prompt}" if system_prompt else prompt
        
        response = self.client.generate_content(full_prompt)
        return response.text
