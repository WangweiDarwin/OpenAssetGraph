"""Test Chat API"""
import httpx
import asyncio

async def test_chat():
    url = "http://localhost:8002/api/chat"
    payload = {"message": "你好，请介绍一下你自己"}
    
    print("Testing Chat API...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    print("-" * 50)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
