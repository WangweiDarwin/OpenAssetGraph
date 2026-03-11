"""Direct LLM test"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from app.core.config import settings
    from app.services.llm import LLMFactory, Message, MessageRole
    
    print("=" * 50)
    print("LLM Configuration:")
    print(f"  Provider: {settings.llm_provider}")
    print(f"  Model: {settings.llm_model}")
    print(f"  GLM API Key: {settings.glm_api_key[:15] if settings.glm_api_key else 'NOT SET'}...")
    print("=" * 50)
    
    try:
        llm = LLMFactory.create_from_settings(settings)
        print("LLM service created successfully")
        
        messages = [
            Message(role=MessageRole.USER, content="Hello, say hi in one word")
        ]
        
        print("Sending request...")
        response = await llm.chat(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print("SUCCESS!")
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
