"""LLM Factory for creating LLM service instances"""
from typing import Optional
from enum import Enum

from .base import LLMConfig, LLMService
from .openai_service import OpenAIService


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GLM = "glm"
    KIMI = "kimi"
    DEEPSEEK = "deepseek"
    CUSTOM = "custom"


class LLMModelConfig:
    """Predefined model configurations"""
    
    MODELS = {
        LLMProvider.OPENAI: {
            "gpt-4": {
                "model": "gpt-4",
                "max_tokens": 8192,
                "base_url": None,
            },
            "gpt-4-turbo": {
                "model": "gpt-4-turbo-preview",
                "max_tokens": 4096,
                "base_url": None,
            },
            "gpt-4o": {
                "model": "gpt-4o",
                "max_tokens": 4096,
                "base_url": None,
            },
            "gpt-3.5-turbo": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 4096,
                "base_url": None,
            },
        },
        LLMProvider.GLM: {
            "glm-4": {
                "model": "glm-4",
                "max_tokens": 8192,
                "base_url": "https://open.bigmodel.cn/api/paas/v4/",
            },
            "glm-4-flash": {
                "model": "glm-4-flash",
                "max_tokens": 4096,
                "base_url": "https://open.bigmodel.cn/api/paas/v4/",
            },
            "glm-4-plus": {
                "model": "glm-4-plus",
                "max_tokens": 8192,
                "base_url": "https://open.bigmodel.cn/api/paas/v4/",
            },
            "glm-4-air": {
                "model": "glm-4-air",
                "max_tokens": 8192,
                "base_url": "https://open.bigmodel.cn/api/paas/v4/",
            },
        },
        LLMProvider.KIMI: {
            "moonshot-v1-8k": {
                "model": "moonshot-v1-8k",
                "max_tokens": 8192,
                "base_url": "https://api.moonshot.cn/v1",
            },
            "moonshot-v1-32k": {
                "model": "moonshot-v1-32k",
                "max_tokens": 32768,
                "base_url": "https://api.moonshot.cn/v1",
            },
            "moonshot-v1-128k": {
                "model": "moonshot-v1-128k",
                "max_tokens": 131072,
                "base_url": "https://api.moonshot.cn/v1",
            },
        },
        LLMProvider.DEEPSEEK: {
            "deepseek-chat": {
                "model": "deepseek-chat",
                "max_tokens": 4096,
                "base_url": "https://api.deepseek.com/v1",
            },
            "deepseek-coder": {
                "model": "deepseek-coder",
                "max_tokens": 4096,
                "base_url": "https://api.deepseek.com/v1",
            },
        },
    }
    
    @classmethod
    def get_model_config(cls, provider: LLMProvider, model_name: str) -> Optional[dict]:
        """Get predefined model configuration"""
        provider_models = cls.MODELS.get(provider, {})
        return provider_models.get(model_name)
    
    @classmethod
    def list_models(cls, provider: Optional[LLMProvider] = None) -> list[str]:
        """List available models"""
        if provider:
            return list(cls.MODELS.get(provider, {}).keys())
        
        all_models = []
        for provider_models in cls.MODELS.values():
            all_models.extend(provider_models.keys())
        return all_models


class LLMFactory:
    """Factory for creating LLM service instances"""
    
    @staticmethod
    def create(
        provider: LLMProvider,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMService:
        """Create an LLM service instance based on provider"""
        
        predefined_config = None
        if model:
            predefined_config = LLMModelConfig.get_model_config(provider, model)
        
        if predefined_config:
            model = predefined_config.get("model", model)
            if base_url is None:
                base_url = predefined_config.get("base_url")
            if max_tokens is None or max_tokens == 4096:
                max_tokens = predefined_config.get("max_tokens", 4096)
        
        config = LLMConfig(
            model=model or "gpt-4-turbo-preview",
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        if provider in [LLMProvider.OPENAI, LLMProvider.GLM, LLMProvider.KIMI, LLMProvider.DEEPSEEK, LLMProvider.CUSTOM]:
            return OpenAIService(config)
        
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def create_from_settings(settings) -> LLMService:
        """Create LLM service from application settings"""
        provider_str = getattr(settings, 'llm_provider', 'openai').lower()
        
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            provider = LLMProvider.OPENAI
        
        api_key = ""
        if provider == LLMProvider.GLM:
            api_key = getattr(settings, 'glm_api_key', '') or getattr(settings, 'openai_api_key', '')
        elif provider == LLMProvider.KIMI:
            api_key = getattr(settings, 'kimi_api_key', '') or getattr(settings, 'openai_api_key', '')
        elif provider == LLMProvider.DEEPSEEK:
            api_key = getattr(settings, 'deepseek_api_key', '') or getattr(settings, 'openai_api_key', '')
        else:
            api_key = getattr(settings, 'openai_api_key', '')
        
        model = getattr(settings, 'llm_model', None) or getattr(settings, 'openai_model', 'gpt-4-turbo-preview')
        
        base_url = getattr(settings, 'llm_base_url', None)
        
        temperature = getattr(settings, 'llm_temperature', 0.7)
        max_tokens = getattr(settings, 'llm_max_tokens', 4096)
        
        return LLMFactory.create(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )
