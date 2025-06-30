#!/usr/bin/env python3
"""
🚀 SuperMCP Multi-Model AI Router System
Universal AI interface with intelligent routing and cost optimization

Features:
- 🔥 All major APIs (OpenAI, Claude, DeepSeek, Perplexity, Google AI)
- 💻 Local models (Llama, Codestral, Ollama)
- 🧠 Intelligent task-based routing
- 💰 Cost optimization with fallbacks
- ⚡ Unified REST API
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import requests
from flask import Flask, request, jsonify
from threading import Thread
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task specialization types"""
    CODE = "code"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CHAT = "chat"
    TRANSLATION = "translation"
    CREATIVE = "creative"
    MATH = "math"
    GENERAL = "general"

class ModelProvider(Enum):
    """Model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    PERPLEXITY = "perplexity"
    GOOGLE = "google"
    LOCAL_OLLAMA = "ollama"
    LOCAL_LLAMACPP = "llamacpp"

@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    provider: ModelProvider
    cost_per_1k_tokens: float
    max_tokens: int
    specializations: List[TaskType]
    priority: int  # Lower = higher priority
    requires_api_key: bool = True
    endpoint: Optional[str] = None

@dataclass
class GenerationRequest:
    """Generation request"""
    prompt: str
    task_type: TaskType = TaskType.GENERAL
    max_tokens: int = 1000
    temperature: float = 0.7
    force_model: Optional[str] = None
    budget_limit: float = 0.0  # 0 = no limit

@dataclass
class GenerationResponse:
    """Generation response"""
    content: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    response_time: float
    error: Optional[str] = None

class MultiModelRouter:
    """Intelligent multi-model router"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.api_keys = self._load_api_keys()
        self.usage_stats = {}
        
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations"""
        return {
            # OpenAI Models
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                provider=ModelProvider.OPENAI,
                cost_per_1k_tokens=0.015,
                max_tokens=4000,
                specializations=[TaskType.ANALYSIS, TaskType.CREATIVE, TaskType.GENERAL],
                priority=2
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                cost_per_1k_tokens=0.001,
                max_tokens=4000,
                specializations=[TaskType.CHAT, TaskType.GENERAL],
                priority=3
            ),
            
            # Anthropic Models
            "claude-3-opus": ModelConfig(
                name="claude-3-opus-20240229",
                provider=ModelProvider.ANTHROPIC,
                cost_per_1k_tokens=0.015,
                max_tokens=4000,
                specializations=[TaskType.ANALYSIS, TaskType.CREATIVE, TaskType.CODE],
                priority=1
            ),
            "claude-3-sonnet": ModelConfig(
                name="claude-3-sonnet-20240229",
                provider=ModelProvider.ANTHROPIC,
                cost_per_1k_tokens=0.003,
                max_tokens=4000,
                specializations=[TaskType.GENERAL, TaskType.ANALYSIS],
                priority=2
            ),
            
            # DeepSeek Models
            "deepseek-coder": ModelConfig(
                name="deepseek-coder",
                provider=ModelProvider.DEEPSEEK,
                cost_per_1k_tokens=0.0014,
                max_tokens=4000,
                specializations=[TaskType.CODE, TaskType.MATH],
                priority=1
            ),
            
            # Perplexity Models
            "perplexity-sonar": ModelConfig(
                name="llama-3.1-sonar-small-128k-online",
                provider=ModelProvider.PERPLEXITY,
                cost_per_1k_tokens=0.0002,
                max_tokens=4000,
                specializations=[TaskType.RESEARCH],
                priority=1
            ),
            
            # Google AI Models
            "gemini-pro": ModelConfig(
                name="gemini-pro",
                provider=ModelProvider.GOOGLE,
                cost_per_1k_tokens=0.0005,
                max_tokens=4000,
                specializations=[TaskType.TRANSLATION, TaskType.GENERAL],
                priority=2
            ),
            
            # Local Models (Free!)
            "llama3-70b": ModelConfig(
                name="llama3:70b",
                provider=ModelProvider.LOCAL_OLLAMA,
                cost_per_1k_tokens=0.0,  # FREE!
                max_tokens=4000,
                specializations=[TaskType.CHAT, TaskType.GENERAL, TaskType.CREATIVE],
                priority=1,
                requires_api_key=False,
                endpoint="http://sam.chat:11434"
            ),
            "codestral": ModelConfig(
                name="codestral:22b",
                provider=ModelProvider.LOCAL_OLLAMA,
                cost_per_1k_tokens=0.0,  # FREE!
                max_tokens=4000,
                specializations=[TaskType.CODE],
                priority=1,
                requires_api_key=False,
                endpoint="http://sam.chat:11434"
            ),
        }
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment"""
        return {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "perplexity": os.getenv("PERPLEXITY_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
        }
    
    def select_model(self, task_type: TaskType, budget_limit: float = 0.0, force_model: Optional[str] = None) -> Optional[str]:
        """Select best model for task with cost optimization"""
        
        if force_model and force_model in self.models:
            return force_model
        
        # Filter models by specialization
        candidates = []
        for model_name, config in self.models.items():
            if task_type in config.specializations:
                # Check if API key available (for paid models)
                if config.requires_api_key:
                    provider_key = config.provider.value
                    if not self.api_keys.get(provider_key):
                        continue
                
                # Check budget limit
                if budget_limit > 0 and config.cost_per_1k_tokens > budget_limit:
                    continue
                
                candidates.append((model_name, config))
        
        if not candidates:
            # Fallback to general models
            for model_name, config in self.models.items():
                if TaskType.GENERAL in config.specializations:
                    if config.requires_api_key:
                        provider_key = config.provider.value
                        if not self.api_keys.get(provider_key):
                            continue
                    candidates.append((model_name, config))
        
        if not candidates:
            return None
        
        # Sort by priority (lower = better), then by cost
        candidates.sort(key=lambda x: (x[1].priority, x[1].cost_per_1k_tokens))
        
        selected = candidates[0][0]
        logger.info(f"Selected model {selected} for task {task_type.value}")
        return selected
    
    async def generate_openai(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int]:
        """Generate using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_keys['openai']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens = result["usage"]["total_tokens"]
                    return content, tokens
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {error_text}")
    
    async def generate_anthropic(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int]:
        """Generate using Anthropic API"""
        headers = {
            "x-api-key": self.api_keys['anthropic'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.anthropic.com/v1/messages",
                                   headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["content"][0]["text"]
                    tokens = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
                    return content, tokens
                else:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {error_text}")
    
    async def generate_deepseek(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int]:
        """Generate using DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_keys['deepseek']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.deepseek.com/v1/chat/completions",
                                   headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens = result["usage"]["total_tokens"]
                    return content, tokens
                else:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error: {error_text}")
    
    async def generate_perplexity(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int]:
        """Generate using Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.api_keys['perplexity']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.perplexity.ai/chat/completions",
                                   headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    tokens = result["usage"]["total_tokens"]
                    return content, tokens
                else:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error: {error_text}")
    
    async def generate_google(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int]:
        """Generate using Google AI API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_keys['google']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    # Google doesn't return token count in all cases, estimate
                    tokens = len(content.split()) * 1.3  # rough estimate
                    return content, int(tokens)
                else:
                    error_text = await response.text()
                    raise Exception(f"Google AI API error: {error_text}")
    
    async def generate_ollama(self, model: str, prompt: str, max_tokens: int, temperature: float) -> Tuple[str, int]:
        """Generate using local Ollama"""
        data = {
            "model": model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            },
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://sam.chat:11434/api/generate",
                                       json=data, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["response"]
                        tokens = len(content.split()) * 1.3  # estimate
                        return content, int(tokens)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")
        except Exception as e:
            raise Exception(f"Ollama connection error: {str(e)}")
    
    async def generate_with_fallback(self, req: GenerationRequest, tried_models: List[str] = None) -> GenerationResponse:
        """Generate response with automatic fallback"""
        if tried_models is None:
            tried_models = []
        
        start_time = time.time()
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Select model (excluding already tried ones)
                available_models = {k: v for k, v in self.models.items() if k not in tried_models}
                if not available_models:
                    return GenerationResponse(
                        content="",
                        model_used="none",
                        tokens_used=0,
                        cost_estimate=0.0,
                        response_time=time.time() - start_time,
                        error="All models exhausted"
                    )
                
                # Temporarily replace models for selection
                original_models = self.models
                self.models = available_models
                selected_model = self.select_model(req.task_type, req.budget_limit, req.force_model)
                self.models = original_models
                
                if not selected_model:
                    return GenerationResponse(
                        content="",
                        model_used="none",
                        tokens_used=0,
                        cost_estimate=0.0,
                        response_time=time.time() - start_time,
                        error="No suitable model available"
                    )
                
                config = self.models[selected_model]
                logger.info(f"Attempting generation with {selected_model} (attempt {attempt + 1})")
                
                # Generate based on provider
                if config.provider == ModelProvider.OPENAI:
                    content, tokens = await self.generate_openai(config.name, req.prompt, req.max_tokens, req.temperature)
                elif config.provider == ModelProvider.ANTHROPIC:
                    content, tokens = await self.generate_anthropic(config.name, req.prompt, req.max_tokens, req.temperature)
                elif config.provider == ModelProvider.DEEPSEEK:
                    content, tokens = await self.generate_deepseek(config.name, req.prompt, req.max_tokens, req.temperature)
                elif config.provider == ModelProvider.PERPLEXITY:
                    content, tokens = await self.generate_perplexity(config.name, req.prompt, req.max_tokens, req.temperature)
                elif config.provider == ModelProvider.GOOGLE:
                    content, tokens = await self.generate_google(config.name, req.prompt, req.max_tokens, req.temperature)
                elif config.provider == ModelProvider.LOCAL_OLLAMA:
                    content, tokens = await self.generate_ollama(config.name, req.prompt, req.max_tokens, req.temperature)
                else:
                    raise Exception(f"Unsupported provider: {config.provider}")
                
                # Success! Calculate cost and time
                cost_estimate = (tokens / 1000) * config.cost_per_1k_tokens
                response_time = time.time() - start_time
                
                # Update usage stats
                if selected_model not in self.usage_stats:
                    self.usage_stats[selected_model] = {"requests": 0, "tokens": 0, "cost": 0.0, "failures": 0}
                
                stats = self.usage_stats[selected_model]
                stats["requests"] += 1
                stats["tokens"] += tokens
                stats["cost"] += cost_estimate
                
                logger.info(f"✅ Generated {tokens} tokens using {selected_model} in {response_time:.2f}s (${cost_estimate:.4f})")
                
                return GenerationResponse(
                    content=content,
                    model_used=selected_model,
                    tokens_used=tokens,
                    cost_estimate=cost_estimate,
                    response_time=response_time
                )
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"❌ Model {selected_model} failed: {error_msg}")
                
                # Add to tried models
                tried_models.append(selected_model)
                
                # Update failure stats
                if selected_model not in self.usage_stats:
                    self.usage_stats[selected_model] = {"requests": 0, "tokens": 0, "cost": 0.0, "failures": 0}
                self.usage_stats[selected_model]["failures"] += 1
                
                # If this was the last attempt or no more models, return error
                if attempt == max_retries - 1 or len(tried_models) >= len(self.models):
                    return GenerationResponse(
                        content="",
                        model_used=selected_model if 'selected_model' in locals() else "unknown",
                        tokens_used=0,
                        cost_estimate=0.0,
                        response_time=time.time() - start_time,
                        error=f"All fallback attempts failed. Last error: {error_msg}"
                    )
                
                logger.info(f"🔄 Trying fallback model (attempt {attempt + 2})")
                await asyncio.sleep(1)  # Brief delay before retry
        
        return GenerationResponse(
            content="",
            model_used="unknown",
            tokens_used=0,
            cost_estimate=0.0,
            response_time=time.time() - start_time,
            error="Maximum retry attempts exceeded"
        )
    
    async def generate(self, req: GenerationRequest) -> GenerationResponse:
        """Generate response using best model with fallback"""
        return await self.generate_with_fallback(req)

# Global router instance
router = MultiModelRouter()

# Flask API
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_available": len(router.models),
        "api_keys_configured": len([k for k, v in router.api_keys.items() if v])
    })

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    models_info = []
    for name, config in router.models.items():
        # Check if model is available
        available = True
        if config.requires_api_key:
            provider_key = config.provider.value
            available = bool(router.api_keys.get(provider_key))
        
        models_info.append({
            "name": name,
            "provider": config.provider.value,
            "cost_per_1k_tokens": config.cost_per_1k_tokens,
            "specializations": [t.value for t in config.specializations],
            "priority": config.priority,
            "available": available,
            "usage_stats": router.usage_stats.get(name, {"requests": 0, "tokens": 0, "cost": 0.0})
        })
    
    return jsonify({
        "models": models_info,
        "total_usage": {
            "total_requests": sum(stats["requests"] for stats in router.usage_stats.values()),
            "total_tokens": sum(stats["tokens"] for stats in router.usage_stats.values()),
            "total_cost": sum(stats["cost"] for stats in router.usage_stats.values())
        }
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate text using optimal model"""
    try:
        data = request.get_json()
        
        req = GenerationRequest(
            prompt=data.get('prompt', ''),
            task_type=TaskType(data.get('task_type', 'general')),
            max_tokens=data.get('max_tokens', 1000),
            temperature=data.get('temperature', 0.7),
            force_model=data.get('force_model'),
            budget_limit=data.get('budget_limit', 0.0)
        )
        
        # Run async generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(router.generate(req))
        loop.close()
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/code', methods=['POST'])
def generate_code():
    """Generate code (specialized endpoint)"""
    try:
        data = request.get_json()
        
        req = GenerationRequest(
            prompt=data.get('prompt', ''),
            task_type=TaskType.CODE,
            max_tokens=data.get('max_tokens', 2000),
            temperature=data.get('temperature', 0.3),
            force_model=data.get('force_model'),
            budget_limit=data.get('budget_limit', 0.0)
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(router.generate(req))
        loop.close()
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/research', methods=['POST'])
def generate_research():
    """Generate research (specialized endpoint)"""
    try:
        data = request.get_json()
        
        req = GenerationRequest(
            prompt=data.get('prompt', ''),
            task_type=TaskType.RESEARCH,
            max_tokens=data.get('max_tokens', 3000),
            temperature=data.get('temperature', 0.5),
            force_model=data.get('force_model'),
            budget_limit=data.get('budget_limit', 0.0)
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(router.generate(req))
        loop.close()
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def generate_analysis():
    """Generate analysis (specialized endpoint)"""
    try:
        data = request.get_json()
        
        req = GenerationRequest(
            prompt=data.get('prompt', ''),
            task_type=TaskType.ANALYSIS,
            max_tokens=data.get('max_tokens', 2000),
            temperature=data.get('temperature', 0.6),
            force_model=data.get('force_model'),
            budget_limit=data.get('budget_limit', 0.0)
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(router.generate(req))
        loop.close()
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def generate_chat():
    """Generate chat response (specialized endpoint)"""
    try:
        data = request.get_json()
        
        req = GenerationRequest(
            prompt=data.get('prompt', ''),
            task_type=TaskType.CHAT,
            max_tokens=data.get('max_tokens', 1000),
            temperature=data.get('temperature', 0.8),
            force_model=data.get('force_model'),
            budget_limit=data.get('budget_limit', 0.0)
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(router.generate(req))
        loop.close()
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    return jsonify({
        "usage_stats": router.usage_stats,
        "total_requests": sum(stats["requests"] for stats in router.usage_stats.values()),
        "total_tokens": sum(stats["tokens"] for stats in router.usage_stats.values()),
        "total_cost": sum(stats["cost"] for stats in router.usage_stats.values()),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🚀 SuperMCP Multi-Model AI Router")
    print("=" * 50)
    print("🔥 External APIs: OpenAI, Claude, DeepSeek, Perplexity, Google AI")
    print("💻 Local Models: Llama, Codestral, Ollama")
    print("🧠 Intelligent routing with cost optimization")
    print("💰 Prioritizes free local models")
    print("=" * 50)
    print("🌐 API Endpoints:")
    print("  GET  /health      - System health")
    print("  GET  /models      - List models")
    print("  GET  /stats       - Usage stats")
    print("  POST /generate    - Generate text")
    print("  POST /code        - Generate code")
    print("  POST /research    - Research tasks")
    print("  POST /analyze     - Analysis tasks")
    print("  POST /chat        - Chat responses")
    print("=" * 50)
    print(f"🎯 Server starting on http://sam.chat:8300")
    print("🔑 Configure API keys in .env file")
    print("⚡ Ready for unified AI access!")
    
    app.run(host='0.0.0.0', port=8300, debug=False)