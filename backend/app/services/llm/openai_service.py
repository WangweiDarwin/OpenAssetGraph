"""OpenAI LLM service implementation"""
import json
from typing import Any, AsyncIterator, Optional

from .base import (
    LLMConfig,
    LLMResponse,
    LLMService,
    Message,
)

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    AsyncOpenAI = None


class OpenAIService(LLMService):
    """OpenAI API implementation"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        
        if not HAS_OPENAI:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        client_kwargs: dict[str, Any] = {}
        if config.api_key:
            client_kwargs["api_key"] = config.api_key
        if config.base_url:
            client_kwargs["base_url"] = config.base_url
        
        self.client = AsyncOpenAI(**client_kwargs)
    
    async def chat(
        self,
        messages: list[Message],
        **kwargs: Any
    ) -> LLMResponse:
        """Send chat completion request to OpenAI"""
        formatted_messages = [msg.to_dict() for msg in messages]
        
        model = kwargs.get("model", self.config.model)
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=kwargs.get("top_p", self.config.top_p),
            frequency_penalty=kwargs.get("frequency_penalty", self.config.frequency_penalty),
            presence_penalty=kwargs.get("presence_penalty", self.config.presence_penalty),
        )
        
        choice = response.choices[0]
        
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason,
            metadata={
                "id": response.id,
                "created": response.created,
            }
        )
    
    async def chat_stream(
        self,
        messages: list[Message],
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Send chat completion request with streaming"""
        formatted_messages = [msg.to_dict() for msg in messages]
        
        model = kwargs.get("model", self.config.model)
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def embed(self, text: str) -> list[float]:
        """Generate text embedding using OpenAI"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        
        return response.data[0].embedding
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        
        return [item.embedding for item in response.data]
    
    async def function_call(
        self,
        messages: list[Message],
        functions: list[dict[str, Any]],
        function_call: str = "auto",
        **kwargs: Any
    ) -> tuple[str, Optional[dict[str, Any]]]:
        """Make a function call through the LLM"""
        formatted_messages = [msg.to_dict() for msg in messages]
        
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=formatted_messages,
            functions=functions,
            function_call=function_call,
            temperature=kwargs.get("temperature", self.config.temperature),
        )
        
        choice = response.choices[0]
        
        if choice.message.function_call:
            function_name = choice.message.function_call.name
            function_args = json.loads(choice.message.function_call.arguments)
            return function_name, function_args
        
        return choice.message.content or "", None
