"""
LLM Client for Groq API integration.
Handles API calls and token tracking.
"""

import os
from typing import Dict, Optional
from groq import Groq
from dotenv import load_dotenv


class LLMClient:
    """
    Simple wrapper around Groq API for story generation.
    Tracks tokens so I know how much each transformation costs.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: Optional[str] = None,
        provider: Optional[str] = None
    ):
        """Set up the LLM client - loads API key from .env if not provided"""
        load_dotenv()
        self.provider = "groq"  # Could support others later
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("PRIMARY_MODEL", "llama-3.3-70b-versatile")
        self.client = Groq(api_key=self.api_key)
        self.total_tokens = 0
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """Send prompt to LLM and get response"""
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if response_format:
            kwargs["response_format"] = response_format
        response = self.client.chat.completions.create(**kwargs)
        if hasattr(response, 'usage'):
            self.total_tokens += response.usage.total_tokens
        return response.choices[0].message.content
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Same as generate but forces JSON output format"""
        return self.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
    
    def get_token_usage(self) -> int:
        """Track how many tokens we've used so far"""
        return self.total_tokens
    
    def estimate_cost(self) -> float:
        """Groq is free right now so cost is always zero"""
        return 0.0  
