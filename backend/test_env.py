import os
print("Testing .env loading...")

# Read .env file directly
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
        print(".env file found, first 500 chars:")
        print(content[:500])
else:
    print(".env file NOT found!")

# Test settings
try:
    from app.core.config import settings
    print("\nSettings loaded:")
    print(f"  llm_provider: {settings.llm_provider}")
    print(f"  llm_model: {settings.llm_model}")
    print(f"  glm_api_key: {settings.glm_api_key[:15] if settings.glm_api_key else 'NOT SET'}...")
except Exception as e:
    print(f"Error loading settings: {e}")
