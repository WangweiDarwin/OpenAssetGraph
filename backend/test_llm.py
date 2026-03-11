"""Test LLM API connection"""
import asyncio
from app.services.llm import LLMFactory, Message, MessageRole
from app.core.config import settings


async def test_llm():
    print("=" * 50)
    print("LLM API Test")
    print("=" * 50)
    print(f"Provider: {settings.llm_provider}")
    print(f"Model: {settings.llm_model}")
    
    if settings.glm_api_key and settings.glm_api_key != "your-glm-api-key-here":
        print(f"GLM API Key: {settings.glm_api_key[:10]}...")
    else:
        print("GLM API Key: Not configured")
    
    print("-" * 50)
    print("Sending test request...")
    
    llm = LLMFactory.create_from_settings(settings)
    
    messages = [
        Message(role=MessageRole.SYSTEM, content="你是一个有帮助的助手。"),
        Message(role=MessageRole.USER, content="请用一句话介绍 OpenAssetGraph 项目。")
    ]
    
    try:
        response = await llm.chat(messages)
        print("-" * 50)
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        print(f"Tokens: {response.usage}")
        print("-" * 50)
        print("SUCCESS: LLM API is working!")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_llm())
