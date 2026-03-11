import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from app.services.llm import LLMFactory, Message, MessageRole
    from app.core.config import settings
    
    print("Creating LLM service...")
    llm = LLMFactory.create_from_settings(settings)
    
    messages = [
        Message(role=MessageRole.USER, content="Say hi")
    ]
    
    print("Sending request to GLM...")
    response = await llm.chat(messages)
    print(f"Response: {response.content}")
    print("SUCCESS!")

asyncio.run(test())
