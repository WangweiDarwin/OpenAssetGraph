"""Base LLM service interface"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Optional


class MessageRole(str, Enum):
    """Message role in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Chat message"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> dict[str, str]:
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class LLMConfig:
    """LLM service configuration"""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60


@dataclass
class ChatContext:
    """Chat conversation context"""
    messages: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    max_tokens: int = 8192
    
    def add_message(self, message: Message) -> None:
        self.messages.append(message)
    
    def add_system_message(self, content: str) -> None:
        self.add_message(Message(role=MessageRole.SYSTEM, content=content))
    
    def add_user_message(self, content: str) -> None:
        self.add_message(Message(role=MessageRole.USER, content=content))
    
    def add_assistant_message(self, content: str) -> None:
        self.add_message(Message(role=MessageRole.ASSISTANT, content=content))
    
    def get_messages(self) -> list[dict[str, str]]:
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        self.messages.clear()
        self.token_count = 0


@dataclass
class LLMResponse:
    """LLM response"""
    content: str
    model: str
    usage: dict[str, int]
    finish_reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMService(ABC):
    """Abstract base class for LLM services"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        **kwargs: Any
    ) -> LLMResponse:
        """Send chat completion request"""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: list[Message],
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Send chat completion request with streaming"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate text embedding"""
        pass
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (approximate)"""
        return len(text.split()) * 2
    
    def build_context(
        self,
        system_prompt: str,
        user_query: str,
        context_data: Optional[dict[str, Any]] = None
    ) -> ChatContext:
        """Build chat context with system prompt and user query"""
        ctx = ChatContext()
        
        full_system_prompt = system_prompt
        if context_data:
            context_str = self._format_context(context_data)
            full_system_prompt = f"{system_prompt}\n\n## Context Data\n\n{context_str}"
        
        ctx.add_system_message(full_system_prompt)
        ctx.add_user_message(user_query)
        
        return ctx
    
    def _format_context(self, data: dict[str, Any], indent: int = 0) -> str:
        """Format context data as readable string"""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_context(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self._format_context(item, indent + 1))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
