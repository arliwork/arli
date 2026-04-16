"""
Universal LLM Client for ARLI
Supports OpenRouter, OpenAI, Anthropic, Ollama
With unified credit-based cost tracking
"""
import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import aiohttp

# Provider configs with credit multipliers
MODEL_REGISTRY = {
    # OpenAI models
    "gpt-4o": {"provider": "openai", "credit_multiplier": 2.5},
    "gpt-4": {"provider": "openai", "credit_multiplier": 3.0},
    "gpt-4o-mini": {"provider": "openai", "credit_multiplier": 0.6},
    "o3-mini": {"provider": "openai", "credit_multiplier": 1.2},
    "gpt-5-mini": {"provider": "openai", "credit_multiplier": 0.6},
    "gpt-5.3-codex": {"provider": "openai", "credit_multiplier": 2.8},
    # Anthropic models
    "claude-3-5-sonnet-20241022": {"provider": "anthropic", "credit_multiplier": 2.0},
    "claude-3-opus-20240229": {"provider": "anthropic", "credit_multiplier": 5.0},
    "claude-haiku-4.5": {"provider": "anthropic", "credit_multiplier": 1.6},
    "claude-sonnet-4.6": {"provider": "anthropic", "credit_multiplier": 4.8},
    # OpenRouter models (can proxy all)
    "deepseek/deepseek-chat": {"provider": "openrouter", "credit_multiplier": 0.3},
    "minimax/minimax-m2.5": {"provider": "openrouter", "credit_multiplier": 0.5},
    "openai/gpt-4o": {"provider": "openrouter", "credit_multiplier": 2.5},
    "anthropic/claude-3.5-sonnet": {"provider": "openrouter", "credit_multiplier": 2.0},
    "google/gemini-2.0-flash-001": {"provider": "openrouter", "credit_multiplier": 1.0},
    "kimi/kimi-k2.5": {"provider": "openrouter", "credit_multiplier": 1.3},
    "thudm/glm-4.5": {"provider": "openrouter", "credit_multiplier": 1.5},
    "qwen/qwen3-8b": {"provider": "openrouter", "credit_multiplier": 0.8},
    # Kimi Code (direct)
    "kimi-k2": {"provider": "kimi", "credit_multiplier": 1.8},
    "kimi-k1.6": {"provider": "kimi", "credit_multiplier": 2.0},
    # Local/Ollama
    "llama3.1": {"provider": "ollama", "credit_multiplier": 0.1},
    "codellama": {"provider": "ollama", "credit_multiplier": 0.1},
    "deepseek-coder": {"provider": "ollama", "credit_multiplier": 0.1},
}

DEFAULT_MODELS = {
    "coding": "kimi-k2",
    "reasoning": "kimi-k2",
    "simple": "google/gemini-3.1-flash",
    "creative": "kimi-k2",
    "default": "kimi-k2",
}


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    credits_used: float
    tokens_prompt: int
    tokens_completion: int
    raw_response: Optional[Dict] = None


class LLMClient:
    """Unified LLM client with credit tracking"""

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        self.kimi_key = os.getenv("KIMI_API_KEY", "")
        self.kimi_base_url = os.getenv("KIMI_BASE_URL", "https://api.kimi.com/coding")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120))
        return self.session

    def _provider_available(self, provider: str) -> bool:
        if provider == "openrouter":
            return bool(self.openrouter_key)
        elif provider == "openai":
            return bool(self.openai_key)
        elif provider == "anthropic":
            return bool(self.anthropic_key)
        elif provider == "ollama":
            # Quick health check
            import urllib.request
            try:
                urllib.request.urlopen(f"{self.ollama_url}/api/tags", timeout=2)
                return True
            except Exception:
                return False
        elif provider == "kimi":
            return bool(self.kimi_key)
        return False

    def resolve_model(self, task_type: str = "default", model: Optional[str] = None) -> str:
        if model and model in MODEL_REGISTRY:
            return model
        fallback = DEFAULT_MODELS.get(task_type, DEFAULT_MODELS["default"])
        info = MODEL_REGISTRY.get(fallback, {"provider": "openrouter"})
        if self._provider_available(info["provider"]):
            return fallback
        # Try any available model
        for m, cfg in MODEL_REGISTRY.items():
            if self._provider_available(cfg["provider"]):
                return m
        raise RuntimeError("No LLM provider configured. Set KIMI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY, or OLLAMA_URL.")

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def _calculate_credits(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        info = MODEL_REGISTRY.get(model, {"credit_multiplier": 1.0})
        mult = info["credit_multiplier"]
        base = (prompt_tokens / 1000) * 1.0 + (completion_tokens / 1000) * 3.0
        return round(base * mult, 4)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        task_type: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[Dict]] = None,
    ) -> LLMResponse:
        resolved = self.resolve_model(task_type, model)
        info = MODEL_REGISTRY.get(resolved, {"provider": "openrouter", "credit_multiplier": 1.0})
        provider = info["provider"]

        prompt_text = json.dumps(messages)
        prompt_tokens = self._estimate_tokens(prompt_text)

        if provider == "openai":
            response = await self._call_openai(resolved, messages, temperature, max_tokens, tools)
        elif provider == "anthropic":
            response = await self._call_anthropic(resolved, messages, temperature, max_tokens, tools)
        elif provider == "kimi":
            response = await self._call_kimi(resolved, messages, temperature, max_tokens, tools)
        elif provider == "ollama":
            response = await self._call_ollama(resolved, messages, temperature, max_tokens)
        else:
            response = await self._call_openrouter(resolved, messages, temperature, max_tokens, tools)

        completion_tokens = self._estimate_tokens(response["content"])
        credits = self._calculate_credits(resolved, prompt_tokens, completion_tokens)

        return LLMResponse(
            content=response["content"],
            model=resolved,
            provider=provider,
            credits_used=credits,
            tokens_prompt=prompt_tokens,
            tokens_completion=completion_tokens,
            raw_response=response.get("raw"),
        )

    async def _call_openai(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict]] = None,
    ) -> Dict:
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not configured")
        session = await self._get_session()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"OpenAI error: {data}")
            content = data["choices"][0]["message"]["content"]
            return {"content": content, "raw": data}

    async def _call_anthropic(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict]] = None,
    ) -> Dict:
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        session = await self._get_session()
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                chat_messages.append(m)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            payload["system"] = system_msg
        if tools:
            payload["tools"] = tools
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"Anthropic error: {data}")
            content = data["content"][0]["text"]
            return {"content": content, "raw": data}

    async def _call_kimi(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict]] = None,
    ) -> Dict:
        if not self.kimi_key:
            raise ValueError("KIMI_API_KEY not configured")
        session = await self._get_session()
        # Kimi Code uses Anthropic-compatible format
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                chat_messages.append(m)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            payload["system"] = system_msg
        if tools:
            payload["tools"] = tools
        async with session.post(
            f"{self.kimi_base_url}/v1/messages",
            headers={
                "Authorization": f"Bearer {self.kimi_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"Kimi error: {data}")
            content = data["content"][0]["text"]
            return {"content": content, "raw": data}

    async def _call_openrouter(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict]] = None,
    ) -> Dict:
        if not self.openrouter_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        session = await self._get_session()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://arli.ai",
                "X-Title": "ARLI",
            },
            json=payload,
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"OpenRouter error: {data}")
            content = data["choices"][0]["message"]["content"]
            return {"content": content, "raw": data}

    async def _call_ollama(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict:
        session = await self._get_session()
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        async with session.post(
            f"{self.ollama_url}/api/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"Ollama error: {data}")
            content = data["message"]["content"]
            return {"content": content, "raw": data}

    def _call_dummy(self, messages: List[Dict[str, str]], task_type: str) -> Dict:
        last_msg = messages[-1]["content"] if messages else "No input"
        if task_type == "coding":
            return {
                "content": f"# Demo code generation for: {last_msg[:80]}\n\n```python\n# Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY for real LLM generation.\ndef demo():\n    pass\n```",
                "raw": {"dummy": True, "task_type": task_type},
            }
        elif task_type == "reasoning":
            return {
                "content": f"# Strategic Plan (DEMO MODE)\n\n1. Analyze requirements for: {last_msg[:80]}\n2. Define success criteria\n3. Allocate resources\n4. Execute iteratively\n\n_Note: Set an LLM API key for real generation._",
                "raw": {"dummy": True, "task_type": task_type},
            }
        else:
            return {
                "content": f"# Agent Response (DEMO MODE)\n\nTask received: {last_msg[:120]}\n\nThis is a simulated response because no LLM API keys are configured. To enable real AI generation, set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY, or OLLAMA_URL.",
                "raw": {"dummy": True, "task_type": task_type},
            }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def get_available_models() -> Dict[str, Any]:
    return {
        "registry": MODEL_REGISTRY,
        "defaults": DEFAULT_MODELS,
        "providers": ["openai", "anthropic", "openrouter", "ollama", "kimi"],
    }
