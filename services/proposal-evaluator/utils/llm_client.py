"""
LLM Client - Unified interface for language model interactions
"""

import asyncio
import json
from typing import Dict, Any, Optional
import httpx
import openai

from .logger import setup_logger

logger = setup_logger(__name__)

class LLMClient:
    """
    Unified client for interacting with various LLM providers
    Supports OpenAI, Anthropic, and local models
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "openai")
        self.model_name = config.get("model", "gpt-4")
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        
        # Initialize provider-specific client
        self._init_client()
        
    def _init_client(self):
        """Initialize the appropriate client based on provider"""
        if self.provider == "openai":
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        elif self.provider == "anthropic":
            # Would initialize Anthropic client here
            pass
        elif self.provider == "local":
            # For local models (Ollama, etc.)
            self.client = httpx.AsyncClient(base_url=self.base_url)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate text using the configured LLM
        
        Args:
            system_prompt: System prompt to set context
            user_prompt: User prompt with the actual request
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == "openai":
                return await self._generate_openai(
                    system_prompt, user_prompt, temperature, max_tokens, **kwargs
                )
            elif self.provider == "anthropic":
                return await self._generate_anthropic(
                    system_prompt, user_prompt, temperature, max_tokens, **kwargs
                )
            elif self.provider == "local":
                return await self._generate_local(
                    system_prompt, user_prompt, temperature, max_tokens, **kwargs
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using OpenAI API"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using Anthropic API"""
        # Implementation would go here for Anthropic Claude
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    async def _generate_local(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using local model (Ollama, etc.)"""
        
        # Format prompt for local model
        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            **kwargs
        }
        
        response = await self.client.post("/api/generate", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output matching a JSON schema
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            schema: JSON schema for the expected output
            temperature: Generation temperature
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON matching the schema
        """
        
        # Add schema instruction to prompts
        schema_instruction = f"\n\nPlease respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        enhanced_system_prompt = system_prompt + schema_instruction
        
        response = await self.generate(
            enhanced_system_prompt,
            user_prompt,
            temperature=temperature,
            **kwargs
        )
        
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("Failed to extract valid JSON from response")
    
    async def batch_generate(
        self,
        prompts: list[tuple[str, str]],  # [(system, user), ...]
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> list[str]:
        """
        Generate multiple responses in parallel
        
        Args:
            prompts: List of (system_prompt, user_prompt) tuples
            temperature: Generation temperature
            max_tokens: Maximum tokens per generation
            **kwargs: Additional parameters
            
        Returns:
            List of generated responses
        """
        
        tasks = [
            self.generate(system, user, temperature, max_tokens, **kwargs)
            for system, user in prompts
        ]
        
        return await asyncio.gather(*tasks)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": self.provider,
            "model": self.model_name,
            "base_url": self.base_url,
            "capabilities": self._get_model_capabilities()
        }
    
    def _get_model_capabilities(self) -> list[str]:
        """Get model capabilities based on provider and model"""
        capabilities = ["text_generation"]
        
        if self.provider == "openai":
            if "gpt-4" in self.model_name:
                capabilities.extend(["long_context", "reasoning", "code_generation"])
            if "vision" in self.model_name:
                capabilities.append("image_understanding")
                
        return capabilities