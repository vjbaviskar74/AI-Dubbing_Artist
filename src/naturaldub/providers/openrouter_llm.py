import os
import requests
from .base import BaseLLMProvider

class OpenRouterLLMProvider(BaseLLMProvider):
    def __init__(self, model: str = "openai/gpt-4o-mini"):
        self.model = model
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
