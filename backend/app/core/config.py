from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FedGuard"

    # Deployment
    DEPLOYMENT_MODE: str = "local" # local or cloud
    ENVIRONMENT: str = "development"
    FRONTEND_PUBLIC_API_BASE_URL: str = "http://localhost:8000"

    # AWS
    AWS_REGION: str = "us-east-1"
    USE_PARAMETER_STORE: bool = False
    PARAMETER_STORE_PREFIX: str = "/fedguard/dev"
    USE_S3_ARTIFACT_STORE: bool = False
    S3_ARTIFACT_BUCKET: str = ""
    S3_ARTIFACT_PREFIX: str = "fedguard/artifacts"
    USE_CLOUDWATCH_LOGS: bool = False
    CLOUDWATCH_LOG_GROUP: str = "/fedguard/backend"

    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str | None = None
    REDIS_URL: str = ""
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    AWS_BEDROCK_MODEL_ID: str | None = None
    AWS_BEDROCK_GUARDRAIL_ID: str | None = None
    AWS_BEDROCK_GUARDRAIL_VERSION: str | None = None
    
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str | None = None
    LLM_API_BASE: str | None = None
    
    COPILOT_MAX_CONTEXT_TOKENS: int = 6000
    COPILOT_MAX_RESPONSE_TOKENS: int = 800
    COPILOT_TEMPERATURE: float = 0.2
    COPILOT_ENABLE_RAG: bool = False
    COPILOT_ENABLE_GUARDRAILS: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
