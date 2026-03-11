from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OpenAssetGraph"
    app_env: str = "development"
    debug: bool = True
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"
    
    database_url: str = "postgresql://oag:oag123@localhost:5432/oag_metadata"
    
    redis_url: str = "redis://localhost:6379/0"
    
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    llm_provider: str = "glm"
    llm_model: str = "glm-4-flash"
    llm_base_url: str = ""
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    
    glm_api_key: str = ""
    kimi_api_key: str = ""
    deepseek_api_key: str = ""
    
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
