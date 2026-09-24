from .base import LLMClient
from app.core.config import settings

class BedrockLLMClient(LLMClient):
    async def generate(self, prompt: str, context: dict | None = None) -> str:
        if not settings.AWS_REGION:
            raise NotImplementedError("Bedrock AWS credentials and region not configured")
        return "Bedrock response placeholder"
