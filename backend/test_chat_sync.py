"""Test Chat API directly"""
import httpx

url = "http://localhost:8002/api/chat"
payload = {"message": "hello"}

print("Testing Chat API...")
print(f"URL: {url}")

try:
    response = httpx.post(url, json=payload, timeout=60.0)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
