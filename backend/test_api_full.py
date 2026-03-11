import httpx
import json

url = "http://localhost:8002/api/chat"
payload = {"message": "hello"}

print("=" * 60)
print(f"Testing: POST {url}")
print(f"Payload: {json.dumps(payload)}")
print("=" * 60)

try:
    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        print(f"\nResponse Headers: {dict(response.headers)}")
        print(f"\nResponse Body:\n{response.text}")
except httpx.ConnectError as e:
    print(f"\nConnection Error: {e}")
except httpx.TimeoutException as e:
    print(f"\nTimeout Error: {e}")
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
