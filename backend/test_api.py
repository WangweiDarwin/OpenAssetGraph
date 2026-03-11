import httpx
import json

url = "http://localhost:8002/api/chat"
payload = {"message": "hello"}

print(f"Testing: POST {url}")
print(f"Payload: {json.dumps(payload)}")

try:
    response = httpx.post(url, json=payload, timeout=60.0)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
