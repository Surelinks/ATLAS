"""
Atlas AI - LLM Service
========================
Abstraction layer that normalises access to multiple LLM providers behind a
single ``LLMService`` interface.  Supported providers:

* **Groq**  – free-tier cloud inference (default)
* **OpenAI** – paid, highest quality
* **Ollama** – self-hosted, fully offline

The active provider is selected via the ``LLM_PROVIDER`` environment variable.
Provider credentials are loaded lazily so the module can be imported during CI
without requiring API keys.

A *singleton* ``SentenceTransformer`` model is cached at module level so that
the 80 MB weights are downloaded and loaded only once per process lifetime.

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton embedding model
# Loaded once per process; all providers share the same instance.
# ---------------------------------------------------------------------------

_embedding_model = None  # type: Any


def _get_embedding_model():
    """Return (and lazily initialise) the shared SentenceTransformer instance."""
    global _embedding_model  # noqa: PLW0603
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415

            _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Loaded embedding model: %s", settings.EMBEDDING_MODEL)
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install it with: pip install sentence-transformers"
            ) from exc
    return _embedding_model


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text completion"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings"""
        pass


class OllamaProvider(LLMProvider):
    """Ollama provider - FREE local models"""
    
    def __init__(self, base_url: str, model: str = "llama3"):
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized Ollama provider with model: {model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using Ollama"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["response"]
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Ollama"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["embedding"]


class GroqProvider(LLMProvider):
    """Groq provider - FREE tier with high limits"""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        logger.info(f"Initialized Groq provider with model: {model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using Groq"""
        async with httpx.AsyncClient() as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def embed(self, text: str) -> List[float]:
        """
        Groq does not yet expose an embeddings endpoint.
        Falls back to the shared ``SentenceTransformer`` instance for
        fast, free, local embeddings (model: all-MiniLM-L6-v2).
        """
        model = _get_embedding_model()
        return model.encode(text).tolist()


class OpenAIProvider(LLMProvider):
    """OpenAI provider - Paid but high quality"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info("Initialized OpenAI provider")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding


class LLMService:
    """
    Main LLM service that auto-selects provider based on config
    """
    
    def __init__(self):
        self._provider = None
    
    @property
    def provider(self) -> LLMProvider:
        """Lazy initialization of provider"""
        if self._provider is None:
            self._provider = self._initialize_provider()
        return self._provider
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize the configured LLM provider"""
        provider_name = settings.LLM_PROVIDER.lower()
        
        if provider_name == "ollama":
            return OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model="llama3"  # or mistral, codellama, etc.
            )
        elif provider_name == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set")
            return GroqProvider(
                api_key=settings.GROQ_API_KEY,
                model="llama-3.3-70b-versatile"  # Fast, powerful, free!
            )
        elif provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text completion"""
        return await self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings"""
        return await self.provider.embed(text)
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        system_prompt: str = "You are a helpful assistant."
    ) -> str:
        """RAG pattern: generate answer using retrieved context"""
        context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context)])
        
        prompt = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
        
        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3  # Lower temp for factual answers
        )


# Global instance
llm_service = LLMService()
