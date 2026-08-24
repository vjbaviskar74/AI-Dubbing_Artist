import os
from groq import Groq
from .base import BaseLLMProvider

class GroqLLMProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama3-70b-8192"):
        self.model = model
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
