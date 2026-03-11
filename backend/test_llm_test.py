import httpx

print("Testing /api/chat/test endpoint...")
print("=" * 50)

try:
    response = httpx.get("http://localhost:8005/api/chat/test", timeout=60.0)
    print(f"Status: {response.status_code}")
    print(f"Response:\n{response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
